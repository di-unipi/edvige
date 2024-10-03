/*
    Script that removes all cards from the column #left,
    then given the height of the column it arranges the cards
    in #left, #center, and #right columns until they are full.
    Then, it discards the remaining cards.

    The code is written in vanilla JavaScript.
*/

// Get the height of the left column
var left_column = document.getElementById('left');
// var col_height = left_column.offsetHeight;
var col_height = 1000;
console.log('Left height: ' + col_height);

// Initialize usage
let used = [0, 0, 0];

// Iterate over left column childs and remove them
let cards = [];
let heights = [];
for (elem of left_column.children) {
    // Check if the element is a card
    if (!elem.classList.contains('card')) {
        height = elem.offsetHeight;
        used[0] += height;
        continue;
    }
    height = elem.offsetHeight;
    cards.push(elem);
    heights.push(height);
}

// Remove cards
for (card of cards) {
    if (!card.classList.contains('card')) {
        continue;
    }
    left_column.removeChild(card);
}

function get_column(column_id) {
    if (column_id == 0) {
        return document.getElementById('left');
    } else if (column_id == 1) {
        return document.getElementById('center');
    } else {
        return document.getElementById('right');
    }
}

let current = 0;
let full = false;
for (let i = 0; i < cards.length; i++) {
    // Get the card
    let card = cards[i];
    let card_height = heights[i];

    // Log
    console.log('Card: n.' + i);
    console.log('Card height: ' + card_height);
    console.log('Used: ' + used);

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
        console.log('Stop inserting after card: ' + i);
        console.log('Remaining cards: ' + cards.length - i);
        break;
    }

    // Insert the card
    get_column(current).appendChild(card);
    used[current] += card_height;

    console.log('Used after insert: ' + used);
}
