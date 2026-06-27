
window.addEventListener("scroll", function () {
    const scrollTop = document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const bar = document.getElementById("progressBar");
    if (bar) bar.style.width = (scrollTop / scrollHeight) * 100 + "%";
});


document.querySelectorAll(".yt-thumb").forEach(function (thumb) {
    thumb.addEventListener("click", function () {
        const vid = thumb.dataset.vid;
        if (!vid) return;


        const iframe = document.createElement("iframe");
        iframe.src = "https://www.youtube.com/embed/" + vid + "?autoplay=1&rel=0";
        iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
        iframe.allowFullscreen = true;


        thumb.innerHTML = "";
        thumb.appendChild(iframe);


        thumb.style.cursor = "default";
    });
});