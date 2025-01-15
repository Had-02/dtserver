$.ajax({
    url: '/api/location/',  // Django에서 설정한 URL
    type: 'POST',
    data: {
        latitude: latitude,
        longitude: longitude,
        csrfmiddlewaretoken: '{{ csrf_token }}'  // CSRF 보호를 위한 토큰
    },
    success: function(response) {
        console.log('위치 데이터 전송 성공:', response);
    },
    error: function(xhr, status, error) {
        console.error('위치 데이터 전송 실패:', error);
    }
});
