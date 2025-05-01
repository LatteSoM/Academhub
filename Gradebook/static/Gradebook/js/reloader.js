

document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href*="download_report"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const originalUrl = window.location.href;
            const downloadUrl = this.href;

            fetch(downloadUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.blob();
                })
                .then(blob => {
                    // Создаем временную ссылку для скачивания
                    const blobUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = blobUrl;
                    a.download = '';
                    document.body.appendChild(a);
                    a.click();

                    // Очистка
                    setTimeout(() => {
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(blobUrl);

                        window.location.href = originalUrl;

                    }, 100);
                })
                .catch(error => {
                    console.error('Download error:', error);
                    alert('Произошла ошибка при скачивании файла');
                });
        });
    });
});