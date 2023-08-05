document.addEventListener("DOMContentLoaded", function(event) {
  var buttons = document.getElementsByClassName("mark-read-btn");
  for(var i=0; i<buttons.length; i++) {
    buttons[i].addEventListener("click", function(e){
      var itemNode = this.parentNode.parentNode.parentNode;
      var id = this.dataset.id;
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var parent = itemNode.parentNode;
        parent.removeChild(itemNode);
        if(parent.childElementCount <= 0)
          location.reload();
      }
      };
      xhttp.open("DELETE", location.href + "api/item/" + id + '/', true);
      xhttp.send();
    });
  }
});
