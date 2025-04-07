var id = setInterval(frame, 1000);

function timeToStr(secs1) {
  mins = secs1/60.0
  secs = (mins - Math.floor(mins)) * 60
  
  secs = Math.floor(secs)
  mins = Math.floor(mins)
  return Number(mins) + ":" + Number(secs) + " Minuten"
}

function frame() {
	diff = Math.floor(Date.now() / 1000) - ts
  if (diff >= max) {
    clearInterval(id)
    document.getElementById("timer").innerHTML = "<button type=\"button\" onClick=\"window.location.reload()\">Mehr Infos</button>"
  } else {
    //Number(max-diff)
    document.getElementById("timer").innerHTML = timeToStr(max-diff) + " Wartezeit für mehr Info"
  }
}

