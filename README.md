ElasticsearchCommand for Splunk
ElasticsearchCommand는 Splunk에서 Elasticsearch 데이터를 직접 검색하고 Splunk 이벤트로 변환할 수 있는 Splunk Custom Command입니다. 

이 도구를 사용하면 두 시스템 간의 통합이 간편해지고, Splunk 검색창에서 Elasticsearch 데이터를 효과적으로 조회할 수 있습니다.

## 주요 기능
1. Elasticsearch 데이터 검색: Elasticsearch 쿼리를 사용하여 데이터를 검색합니다.
2. 대량 데이터 처리: search_after를 활용해 페이징 방식으로 대량 데이터를 효율적으로 처리합니다.
3. Splunk 이벤트 변환: Elasticsearch 데이터를 Splunk 이벤트 형식으로 변환합니다.
4. 사용자 정의 옵션: 다양한 검색 조건과 정렬 필드를 설정할 수 있습니다.

## 사용 예제
| elasticsearch index="my_index" query='{"match_all": {}}' size=500 sort_fields="@timestamp" max_results=10000
