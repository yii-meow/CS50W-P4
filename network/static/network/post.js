// document.addEventListener("DOMContentLoaded", () => {
//     // Load All Posts On Default
//     document.querySelector(".profile").style.display = "none"
//
//     // Send Post Event
//     document.querySelector("#post").onsubmit = () => {
//         fetch("/posting", {
//             method: "POST",
//             body: JSON.stringify({
//                 content: document.querySelector("#content").value
//             })
//         })
//             .then(response => response.json())
//             .then(result => {
//                 console.log(result);
//             })
//             .catch(err => {
//                 console.log(err);
//             })
//     }
//
//     // Check Profile Event
//     document.querySelector("#profile").onclick = () => {
//         const user_id = document.querySelector("#profile").dataset.id;
//         fetch(`profile/${user_id}`)
//             .then(response => response.json())
//             .then(result => {
//                 document.querySelector(".all_posts").style.display = "none"
//                 document.querySelector(".profile").style.display = "block"
//                 document.querySelector("#username").innerHTML = result.username;
//
//                 console.log(result)
//             })
//             .catch(err => {
//                 console.log("Error: ", err)
//             })
//     }
// })