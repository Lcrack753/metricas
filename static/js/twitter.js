addClassToElementById('item-twitter', 'active');

// document.addEventListener('DOMContentLoaded', () => {
//     fetch('{% url "api_twitter" %}')
//         .then(response => response.json())
//         .then(data => {
//             populate(data);
//         })
//         .catch(error => {
//             console.error('Error fetching data:', error);
//         });
// });

// function populate(data) {
//     let header = document.querySelector('.header');
//     header.innerHTML = `
//         <h1>Header</h1>
//     `
// }