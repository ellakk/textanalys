// Declare globals to satisfy standardJS
/* global XMLHttpRequest FormData alert $ */

/**
 * Add method to count keys in object.
 */
Object.size = function (obj) {
  var size = 0; var key
  for (key in obj) {
    if (obj.hasOwnProperty(key)) size++
  }
  return size
}

/**
 * This code runs after the html code has finished loading.
 */
window.addEventListener('load', () => {
  // take over the forms submit event.
  var form = document.getElementById('docxForm')
  form.addEventListener('submit', (event) => {
    event.preventDefault()
    $('#submitButton').text('Analyserar')
    $('#submitButton').attr('disabled', true)
    $('#turnInSpinner').show()
    sendData()
  })
  $('#ignoreAndSubmit').click(missionComplete)
  $('#turnInSpinner').hide()
  $('#inlamning-ruta').hide()
  $('#lamna-in').click(() => {
    $('#inlamning-ruta').show()
    $('#lamna-in').hide()
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
 * Notify the user that the assignment is submitted
 */
const missionComplete = () => {
  alert('Du klarade det! Tested är över! :)')
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
  var document = $('#document')

  // Clear the table
  table.find('button').remove()

  if (data.data.has_errors) {
    data.data.errors.forEach((row) => {
      table.append('<button type="button" class="error-rows list-group-item-danger list-group-item-action" data-start="' + row.start + '"' +
                   ' data-end="' + row.end + '">' + row.message + '</button>')
    })
    document.text(data.data.report)
    highlightErrors()
    changeCursorOnError()
    $('#analys-modal').modal('show')
  } else {
    missionComplete()
  }
  $('#submitButton').attr('disabled', false)
  $('#turnInSpinner').hide()
  $('#submitButton').text('Lämna in')
}

/**
* Highlight error on click, uses markjs
**/
const highlightErrors = () => {
  $('.error-rows').click(
    function () {
      $('#document').unmark()
      var range = {}
      range.length = $(this).data('end') - $(this).data('start')
      range.start = $(this).data('start')
      $('#document').markRanges([range])
      $('.error-rows').removeClass('active')
      $(this).addClass('active')
    }
  )
}

/**
 * Change cursor when hovering a error in the table so it looks clickable.
 **/
const changeCursorOnError = () => {
  $('.error-rows').hover(
    function () {
      $(this).css('cursor', 'pointer')
    }, function () {
      $(this).css('cursor', 'auto')
    }
  )
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
