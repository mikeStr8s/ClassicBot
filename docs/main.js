/********************************************************************************
 Default function on page load, fills the ContentContainer Div on index.html with
 description text of the website's functions.
 This also handles the click functions for the Nav Menu.
 @return none
 ********************************************************************************/
function def() {
    //On Webpage load's the default text to ContentContainer Container Div
    $('#ContentContainer').load('onload.html #loadstuff');
    $(home).addClass("using").siblings("a").removeClass("using");
    //Handler for a click even on a piece of the Nav Menu
    $("div a").click(function () {
        //If the Home item is clicked
        if (this.id === "about") {
            //load in the character comparison div from the Char file
            $('#ContentContainer').load('onload.html #loadstuff');
        }
        //apply using class to the clicked nav menu item and remove using from other
        $(this).addClass("using").siblings("a").removeClass("using");
    });
}

//Preforms 'def' funtion on page load.
window.onload = def;