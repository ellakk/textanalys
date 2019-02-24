window.addEventListener("load", () => {
  const sendData = () => {
    var XHR = new XMLHttpRequest();

    var formData = new FormData();
    formData.append("file", document.getElementById("docxSelector").files[0]);


    // Define what happens on successful data submission
    XHR.addEventListener("load", function(event) {
      alert(event.target.responseText);
    });

    // Define what happens in case of error
    XHR.addEventListener("error", function(event) {
      alert("Oops! Something went wrong.");
    });

    XHR.open("POST", "http://127.0.0.1:5000/api/docx");
    XHR.send(formData);
  }

  var form = document.getElementById("docxForm");

  // take over the forms its submit event.
  form.addEventListener("submit", function(event) {
    event.preventDefault();

    sendData();
  });
});
