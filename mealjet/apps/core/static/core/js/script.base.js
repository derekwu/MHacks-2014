

$(document).ready(function(){

$('#accord-one').show();



  $('#accordion').on('show.bs.collapse', function () {
      $('#accordion .in').collapse('hide');
  });

$('.accordion-toggle').on('click',function(e){
    if($(this).parents('.panel').children('.panel-collapse').hasClass('in')){
        e.stopPropagation();
    }
});




}); //END OF DOCUMENT READY




function addExpTitle() {

    var elt = $('#cc_exp_title');
    elt.removeClass('has-success has-error');

    if(!paymentFormFlags['cc_exp_year'] &&
        !paymentFormFlags['cc_exp_month'] )
    {
        elt.addClass('has-success');
    }

    if(paymentFormFlags['cc_exp_year'] == 1 ||
        paymentFormFlags['cc_exp_month'] == 1)
    {
        elt.addClass('has-error');
    }

}

function addError(elt, success, err) {
    elt.removeClass(success + ' ' + err);
    elt.addClass(err);
    elt.children('.glyphicon-ok').addClass('hide');
    elt.children('.glyphicon-remove').removeClass('hide');
}

function addSuccess(elt, success, err) {

    elt.removeClass(success + ' ' + err);
    elt.addClass(success);
    elt.children('.glyphicon-remove').addClass('hide');
    elt.children('.glyphicon-ok').removeClass('hide');
}

function addDefault(elt, success, err) {
  elt.removeClass(success + ' ' + err);
  elt.children('.glyphicon-ok').addClass('hide');
  elt.children('.glyphicon-remove').addClass('hide');
}

