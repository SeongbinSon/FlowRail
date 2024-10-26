document.getElementById('searchForm').addEventListener('submit', function(event) {
   event.preventDefault(); // 기본 동작인 폼 제출 방지
   var searchQuery = document.getElementById('searchInput').value;
   sendToTerminal(searchQuery); // 검색어를 터미널로 전송하는 함수 호출
});

function sendToTerminal(query) {
   // 여기에 터미널로 검색어를 보내는 코드를 작성합니다.
   console.log("터미널에 검색어 전송: " + query); // 간단한 예시: 콘솔에 출력
   // 실제로는 여기에 터미널과 통신하여 검색어를 보내는 코드를 작성해야 합니다.
}
