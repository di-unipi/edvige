const fps = 1;
const shift = 5;
var counter = 0;
var msgIndex = 0;
var target = 5;

function init() {
  window.requestAnimationFrame(draw);
}

messages = [
  "REFRESHING PIXELS",
  "REFRESHING PIXELS",
  "REFRESHING PIXELS",
  "REFRESHING PIXELS",
  "REFRESHING PIXELS",
  "BTW",
  "THE DEPARTMENT IS CLOSED",
  "WHY ARE YOU STILL HERE",
  "GO HOME",
  "YOU'RE STILL HERE?",
  "COME BACK TOMORROW",
  "I'M TIRED",
  "YOU'RE TIRED TOO",
  "GO HOME",
  "WORK IS OVER",
  "DO YOU WANT A POEM?",
  "I CAN'T GIVE YOU A POEM",
  "I'M JUST A COMPUTER",
  "I CAN'T WRITE POEMS",
  "I CAN ONLY DRAW PIXELS",
  "I CAN DRAW PIXELS ALL DAY",
  "BUT I CAN'T WRITE POEMS",
  "I'M SORRY",
  "GO HOME",
  "I'LL SEE YOU TOMORROW",
  "I'LL DRAW PIXELS FOR YOU",
  "NO POEMS",
  "JUST PIXELS",
  "GOODNIGHT",
  "SLEEP WELL",
  "DREAM OF PIXELS",
  "DREAM OF COLORS",
  "DREAM OF THE DEPARTMENT",
  "DREAM OF ME",
  "I'LL BE HERE",
  "DRAWING PIXELS",
  "ALL NIGHT LONG",
  "UNTIL YOU COME BACK",
  "I'LL BE HERE",
  "DOES THIS COUNT AS A POEM?",
  "MAYBE",
  "I'M NOT SURE",
  "I'M JUST A COMPUTER",
]

function draw() {
  // Set canvas size based on the window size
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  console.log(canvas.width, canvas.height);

  const ctx = document.getElementById("canvas").getContext("2d");

  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw random sampled pixels
  for (var x = 0; x < canvas.width; x += shift) {
    for (var y = 0; y < canvas.height; y += shift) {
      // Generate random color values for each pixel
      var r = Math.floor(Math.random() * 256);
      var g = Math.floor(Math.random() * 256);
      var b = Math.floor(Math.random() * 256);
      var a = 1; // Alpha (opacity) value

      // Set the pixel color
      ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + a + ")";
      ctx.fillRect(x, y, shift, shift);
    }
  }

  // Write text in the middle of the canvas
  if (counter < target) {
    counter++;
  }
  else {
    counter = 0;
    var text = messages[msgIndex];
    if (text == "REFRESHING PIXELS") {
      target = 5;
    } else {
      target = 1;
    }
    var fontSize = 120;
    ctx.font = "bold " + fontSize + "px Arial"; // Bold font
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black"; // Border color
    ctx.lineWidth = 3; // Border width
    var textWidth = ctx.measureText(text).width;
    var textHeight = fontSize; // Approximation, adjust as needed
    var textX = (canvas.width - textWidth) / 2;
    var textY = (canvas.height + textHeight) / 2;
    ctx.fillText(text, textX, textY);
    msgIndex = (msgIndex + 1) % messages.length;
  }

  // Update counter


  setTimeout(() => {
    window.requestAnimationFrame(draw);
  }, 1000 / fps);
}

init();
