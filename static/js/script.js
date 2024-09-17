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

// Iterate over left column childs and remove them
let cards = [];
let heights = [];
for (card of left_column.children) {
    height = card.offsetHeight;
    cards.push(card);
    heights.push(height);
}

// Remove cards
for (card of cards) {
    left_column.removeChild(card);
}

// Iterate over cards
let used_left = 0;
let used_center = 0;
let used_right = 0;

for (let i = 0; i < cards.length; i++) {
    // Get the card
    let card = cards[i];
    let card_height = heights[i];

    // Log
    console.log('Card: n.' + i);
    console.log('Card height: ' + card_height);
    console.log('Used left: ' + used_left);
    console.log('Used center: ' + used_center);
    console.log('Used right: ' + used_right);

    // Check if the card fits in the left column
    if (used_left + card_height <= col_height) {
        left_column.appendChild(card);
        used_left += card_height;
    } else if (used_center + card_height <= col_height) {
        document.getElementById('center').appendChild(card);
        used_center += card_height;
    } else if (used_right + card_height <= col_height) {
        document.getElementById('right').appendChild(card);
        used_right += card_height;
    } else {
        console.log('Discarding card: ' + card);
    }
}
