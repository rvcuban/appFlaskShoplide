function showLoader() {
  const loader = document.getElementById("loader");
  loader.style.display = "block";
}

function hideLoader() {
  const loader = document.getElementById("loader");
  loader.style.display = "none";
}

window.addEventListener("load", hideLoader);

document.querySelector("form").addEventListener("submit", (e) => {
  e.preventDefault();
  showLoader();
  setTimeout(() => {
    e.target.submit();
  }, 1000);
});
