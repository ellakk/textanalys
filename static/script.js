// Declare globals to satisfy standardJS
/* global XMLHttpRequest FormData $ */

/**
 * This code runs after the html code has finished loading.
 */
window.addEventListener('load', () => {
  // take over the forms submit event.
  var form = document.getElementById('docxForm')
  form.addEventListener('submit', (event) => {
    event.preventDefault()
    sendData()
  })
})

/**
 * Create and dispatches a bootstrap alert signaling danger/error.
 */
const sendAlert = (message) => {
  var alert = $('<div class="alert alert-danger" role="alert">' +
                '<button type="button" class="close" data-dismiss="alert" ' +
                'aria-label="Close"><span aria-hidden="true">&times;</span>' +
                '</button>' + message + '</div>')
  $('.container').prepend(alert)
  window.setTimeout(() => {
    $('.alert').fadeTo(500, 0).slideUp(500, () => {
      $(this).remove()
    })
  }, 4000)
}

/**
 * Process the API response.
 */
const processData = (JSONdata) => {
  var data = JSON.parse(JSONdata)

  if (data.code !== 200) {
    sendAlert(data.message)
    return
  }

  var table = $('#analysisTable')
  var tableCaption = $('#analysisTableCaption')

  // Clear the table
  table.find('tbody tr').remove()

  if (data.data) {
    data.data.forEach((row) => {
      table.append('<tr><td>' + row.start + '-' + row.end + '</td><td>' + row.message + '</td></tr>')
    })
  }
  tableCaption.text(data.message)
}

/**
 * Sends the .docx file to the API for processing.
 */
const sendData = () => {
  var XHR = new XMLHttpRequest()

  var formData = new FormData()
  formData.append('file', document.getElementById('docxSelector').files[0])

  // Define what happens on successful data submission
  XHR.addEventListener('load', (event) => {
    processData(event.target.responseText)
  })

  // Define what happens in case of error
  XHR.addEventListener('error', (event) => {
    sendAlert('Oj! Något gick åt skogen.')
  })

  XHR.open('POST', 'http://127.0.0.1:5000/api/docx')
  XHR.send(formData)
}
