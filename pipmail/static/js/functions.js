function confirmDelete() {
    var agree = confirm("Are you sure you want to delete this item?");
    if (agree) return true;
    else return false;
}

function updateInput(divId, value) {
    document.getElementById(divId).value = value;
}

// function getURLParameter(name) {document.getElementById('lol').innerText = "Some random text.";
//     return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null
// }