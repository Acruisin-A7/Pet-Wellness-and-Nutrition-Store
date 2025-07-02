function filterVeterinarians() {
    var input = document.getElementById("search").value.toLowerCase();
    var cards = document.getElementsByClassName("vet-card");

    for (var i = 0; i < cards.length; i++) {
        var name = cards[i].getElementsByTagName("h3")[0].innerText.toLowerCase();
        var specialization = cards[i].getElementsByTagName("p")[0].innerText.toLowerCase();

        if (name.includes(input) || specialization.includes(input)) {
            cards[i].style.display = "block";
        } else {
            cards[i].style.display = "none";
        }
    }
}
