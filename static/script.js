// Declare globals to satisfy standardJS
/* global XMLHttpRequest FormData alert $ */

window.addEventListener('load', () => {
  const processData = (JSONdata) => {
    var data = JSON.parse(JSONdata)
    var table = $('#analysisTable')
    var tableCaption = $('#analysisTableCaption')

    // Clear the table
    table.find('tbody tr').remove()

    if (data.data) {
      data.data.forEach((row) => {
        table.append('<tr><td>' + (row.headline ? row.headline : 'Ingen') + '</td><td>' + row.message + '</td></tr>')
      })
    }
    tableCaption.text(data.message)
  }

  const sendData = () => {
    var XHR = new XMLHttpRequest()

    var formData = new FormData()
    formData.append('file', document.getElementById('docxSelector').files[0])

    // Define what happens on successful data submission
    XHR.addEventListener('load', (event) => {
      alert(event.target.responseText)
      processData(event.target.responseText)
    })

    // Define what happens in case of error
    XHR.addEventListener('error', (event) => {
      alert('Oj! Något gick åt skogen')
    })

    XHR.open('POST', 'http://127.0.0.1:5000/api/docx')
    XHR.send(formData)
  }

  var form = document.getElementById('docxForm')

  // take over the forms its submit event.
  form.addEventListener('submit', function (event) {
    event.preventDefault()
    sendData()
  })
})
