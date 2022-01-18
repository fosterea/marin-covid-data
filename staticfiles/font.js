//This program is supposed to make the fonts larger on phones and smaller on computers

var buttons;

document.addEventListener("DOMContentLoaded", function () {

  //Selects the document objects
  let body = document.querySelector("body");
  buttons = document.querySelectorAll(".btn");
  let pageEnd = document.querySelector(".page-end");
  let shs = document.querySelectorAll("sh");

  if (navigator.userAgent.match(/Android/i) //I copied this if statement from https://redstapler.co/detect-mobile-device-with-javascript/
    || navigator.userAgent.match(/webOS/i) //This if statment is true if the website is being run in a mobile browser
    || navigator.userAgent.match(/iPhone/i)
    || navigator.userAgent.match(/iPad/i)
    || navigator.userAgent.match(/iPod/i)
    || navigator.userAgent.match(/BlackBerry/i)
    || navigator.userAgent.match(/Windows Phone/i)) {

    //Sets the font-size of the page if on mobile
    body.style.fontSize = "1.4vh";
    style(buttons, '1.3vh');
    pageEnd.style.fontSize = '1.3vh';
    style(shs, '24pt')
  } else {
    //Sets the font-size of the page if not on mobile
    body.style.fontSize = "12";
    style(buttons, '11pt');
    pageEnd.style.fontSize = '11pt';
  }
});

//Sets the font-size of an array to the fontSize you provide id
function style(buttons, fontSize) {
  for (var button of buttons) {
    button.style.fontSize = fontSize;
  }
}