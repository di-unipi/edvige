/*
    Script that removes all cards from the column #left,
    then given the height of the column it arranges the cards
    in #left, #center, and #right columns until they are full.
    Then, it discards the remaining cards.

    The code is written in vanilla JavaScript.
*/

// Column getter
function get_column(column_id) {
  if (column_id == 0) {
    return document.getElementById("left");
  } else if (column_id == 1) {
    return document.getElementById("center");
  } else {
    return document.getElementById("right");
  }
}

function arrange_cards() {
  // Get the height of the left column
  var left_column = get_column(0);
  // var col_height = left_column.offsetHeight;
  var col_height = 1000;
  console.log("Left height: " + col_height);

  // Initialize usage
  let used = [0, 0, 0];
  for (let column_id = 0; column_id < 3; column_id++) {
    let column = get_column(column_id);
    for (elem of column.children) {
      // Check if class is "special-card"
      if (elem.classList.contains("special-card")) {
        let height = elem.offsetHeight;
        used[column_id] += height;
        console.log(
          "Column " + column_id + " used after special card: " + used,
        );
      }
    }
  }

  // Iterate over left column childs and remove them
  let cards = [];
  let heights = [];
  for (elem of left_column.children) {
    // Check if the element is a special card
    if (elem.classList.contains("special-card")) {
      console.log("Special card found");
      continue;
    }
    let height = elem.offsetHeight;
    cards.push(elem);
    heights.push(height);
  }

  // Remove cards
  for (let card of cards) {
    if (!card.classList.contains("card")) {
      continue;
    }
    left_column.removeChild(card);
  }

  let current = 0;
  let full = false;
  for (let i = 0; i < cards.length; i++) {
    // Get the card
    let card = cards[i];
    let card_height = heights[i];

    // Log
    console.log("Card: n." + i);
    console.log("Card height: " + card_height);
    console.log("Used: " + used);

    // Check if there are free columns
    while (used[current] + card_height > col_height) {
      current++;
      if (current >= 3) {
        full = true;
        break;
      }
    }

    // Check if the columns are full
    if (full) {
      console.log("Stop inserting after card: " + i);
      console.log("Remaining cards: " + cards.length - i);
      break;
    }

    // Remove invisible class from card
    card.classList.remove("invisible");

    // Insert the card
    get_column(current).appendChild(card);
    used[current] += card_height;

    console.log("Used after insert: " + used);
  }
}

Promise.all(
  Array.from(document.images)
    .filter((img) => !img.complete)
    .map(
      (img) =>
        new Promise((resolve) => {
          img.onload = img.onerror = resolve;
        }),
    ),
).then(() => {
  console.log("All images loaded, running the arrangement script.");
  arrange_cards();
});
