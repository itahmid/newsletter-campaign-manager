function confirmDelete() {
    var agree = confirm("Are you sure you want to delete this item?");
    if (agree) return true;
    else return false;
}

function updateInput(divId, value) {
    document.getElementById(divId).value = value;
}
