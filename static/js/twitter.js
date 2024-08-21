addClassToElementById('item-twitter', 'active');

function call_api(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            populate(data);
            // cargar grafico en div con id=graph1
            loadChart(data.tweets);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function populate(data) {
    let header = document.querySelector('.header');
    header.innerHTML = `
        <div>
        <img src='${data.profile.image}'>
        <div class="txt roboto-bold-italic">${data.profile.username}</div>
        </div>
    `;
    header.appendChild(header_item('Followers', data.profile.stats.followers, 'nf nf-oct-people'));
    header.appendChild(header_item('Likes', data.profile.stats.likes, 'nf nf-md-hand_heart_outline'));
    header.appendChild(header_item('Tweets', data.profile.stats.tweets, 'nf nf-md-page_next'));
    header.appendChild(header_item('Avg Likes', data.profile.stats.avgLikes, 'nf nf-md-hand_heart_outline'));
    header.appendChild(header_item('Avg Comments', data.profile.stats.avgComments, 'nf nf-cod-comment_discussion'));
    header.appendChild(header_item('Avg Retweets', data.profile.stats.avgRetweets, 'nf nf-fa-square_twitter'));
    header.appendChild(header_item('Avg Quotes', data.profile.stats.avgQuotes, 'nf nf-md-comment_quote'));

    populate_tweets(data.tweets);
}

function header_item(txt, num, icon) {
    let div = document.createElement('div');
    div.innerHTML = `
        <i class="${icon}"></i>
        <div class="num roboto-bold">${num}</div>
        <div class="txt roboto-regular-italic">${txt}</div>
    `;
    return div;
}

function populate_tweets(tweets) {
    tweets.forEach(function (element) {
        let databody = document.getElementById('databody');
        databody.appendChild(tweet_item(element));
    });
}

function tweet_item(tweet) {
    // Crear el contenedor principal
    let div = document.createElement('div');
    
    // Construir el contenido HTML de manera condicional
    let tweetContent = `
        <div class="tweet">
            <div class="tweet-header">
                <img src="${tweet.user.avatar}" alt="Profile Picture">
                <div class="roboto-bold-italic">${tweet.user.username}</div>
                <a href="${tweet.url}" target="_blank"><i class="nf nf-fa-external_link"></i></a>
            </div>
            <div class="tweet-text roboto-regular">
                ${tweet.text}
            </div>
    `;
    
    // Añadir la imagen del tweet si existe
    if (tweet.picture) {
        tweetContent += `<img src="${tweet.picture}" alt="Tweet Image">`;
    }
    
    // Añadir el resto del contenido
    tweetContent += `
            <div class="tweet-stats roboto-bold-italic">
                <div class="retweets">${tweet.statistics.retweets} retweets</div>
                <div class="likes">${tweet.statistics.likes} likes</div>
                <div class="comments">${tweet.statistics.comments} comments</div>
                <div class="quotes">${tweet.statistics.quotes} quotes</div>
            </div>
        </div>
    `;
    
    // Asignar el contenido HTML al div
    div.innerHTML = tweetContent;
    
    return div;
}



function loadChart(tweets) {
    // Limitar a los últimos 10 tweets
    const lastTweets = tweets.slice(0, 10);

    // Extraer las cantidades de retweets y las primeras 10 letras de los textos de los tweets
    const retweets = lastTweets.map(tweet => tweet.statistics.retweets);
    const labels = lastTweets.map(tweet => {
        // Tomar las primeras 10 letras del texto del tweet
        return tweet.text.length > 10 ? tweet.text.substring(0, 10) + '...' : tweet.text;
    });

    // Configurar el gráfico de Chart.js
    const ctx = document.getElementById('retweetsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: retweets,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false // Desactiva la leyenda
                },
                title: {
                    display: true, // Muestra el título
                    text: 'Retweets', // El texto del título
                    padding: {
                        top: 10,
                        bottom: 30
                    },
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        // Rotar las etiquetas para mejor visualización si es necesario
                        autoSkip: true,
                        maxRotation: 90,
                        minRotation: 45,
                    }
                },
                y: {
                    type: 'logarithmic',
                    beginAtZero: true,
                    display: true, // Mantener los números en el eje y visibles
                    ticks: {
                        callback: function(value, index, values) {
                            // Ajusta las etiquetas del eje y para la escala logarítmica
                            return Number(value).toLocaleString();
                        }
                    }
                }
            }
        }
    });
}
