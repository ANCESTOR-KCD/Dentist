const images = [
  "/static/images/background.webp",
  "/static/images/selfie.webp",
  "/static/images/smile.webp",
];
let current = 0;
const bg = document.getElementById("bgSlideshow");
bg.style.backgroundImage = `url(${images[0]})`;

setInterval(() => {
  current = (current + 1) % images.length;
  bg.style.backgroundImage = `url(${images[current]})`;
}, 5000);
