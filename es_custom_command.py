# -*- coding: utf-8 -*-
import os, sys
import json
import requests
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
import datetime
from time import time

# 로그 설정
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

@Configuration()
class ElasticsearchCommand(GeneratingCommand):
    # Splunk에서 명령어 옵션 정의
    index = Option(require=True)  # Elasticsearch 인덱스
    query = Option(require=True)  # Elasticsearch 쿼리
    size = Option(require=False, default=1000, validate=validators.Integer())  # 한 번에 검색할 결과 개수
    sort_fields = Option(require=False, default='@timestamp')  # 정렬 필드
    max_results = Option(require=False, default=10000, validate=validators.Integer())  # 최대 검색 결과 개수

    def generate(self):
        try:
            # Elasticsearch URL 설정
            es_url = 'http://localhost:9200'
            auth = ('ID', 'PASSWORD')

            # 옵션들을 사용해 Elasticsearch 쿼리 생성
            logging.debug("Parsing query: {}".format(self.query))
            try:
                es_query = json.loads(self.query)  # JSON 형식 쿼리 본문
            except json.JSONDecodeError as e:
                raise RuntimeError("Invalid JSON format in query: {}".format(e))

            sort_fields_list = self.sort_fields.split(",") if self.sort_fields else []  # 정렬 필드 리스트
            if not sort_fields_list:
                raise RuntimeError("Sort fields are required for search_after pagination.")
            search_after_values = None  # 초기 search_after 값

            results_count = 0  # 결과 개수

            # Elasticsearch 쿼리 반복 (search_after로 페이징 처리)
            while results_count < int(self.max_results):
                try:
                    # 쿼리 본문 설정
                    body = {
                        "size": int(self.size),
                        "query": es_query,
                        "sort": [{field: "desc"} for field in sort_fields_list]
                    }
                    if search_after_values:
                        body['search_after'] = search_after_values

                    logging.debug("Query body: {}".format(body))

                    # Elasticsearch에 쿼리 수행
                    response = requests.post(
                        url="{}/{}/_search".format(es_url, self.index),
                        auth=auth,
                        headers={"Content-Type": "application/json"},
                        json=body
                    )

                    if response.status_code != 200:
                        raise RuntimeError("Elasticsearch query error: {}".format(response.text))

                    response_json = response.json()
                    hits = response_json['hits']['hits']

                    if not hits:
                        logging.debug("No more results found, breaking loop")
                        break  # 더 이상 결과가 없으면 루프 종료

                    for hit in hits:
                        # Elasticsearch의 _source에서 개별 필드를 분리하여 반환
                        source = hit['_source']
                        event = {'_raw': json.dumps(source)}
                        for key, value in source.items():
                            event[key] = value  # 개별 필드를 추가하여 Splunk에 반환
                        yield event

                    results_count += len(hits)
                    logging.debug("Results count: {}".format(results_count))
                    search_after_values = hits[-1].get('sort')  # 마지막 문서의 sort 값으로 갱신

                    if not search_after_values:
                        logging.debug("No search_after value found, breaking loop")
                        break

                except requests.RequestException as e:
                    logging.error("Elasticsearch query error: {}".format(e))
                    raise RuntimeError("Elasticsearch query error: {}".format(e))

        except Exception as e:
            logging.error("An unexpected error occurred: {}".format(e))
            raise RuntimeError("An unexpected error occurred: {}".format(e))

if __name__ == "__main__":
    dispatch(ElasticsearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
