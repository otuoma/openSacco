/**
 * Created by Shivala DS LTD on 7/27/2017.
 */


$(document).ready(function () {

    var fixedAmount = document.getElementById("fixedAmount");
    var amountPaid = document.getElementById("amountPaid");

    $('#amountPaid').val(fixedAmount);

    // Start accordions script
    var acc = document.getElementsByClassName("accordion-folder");
    var i;

    for (i = 0; i < acc.length; i++) {
      acc[i].onclick = function() {
        this.classList.toggle("active");
        var panel = this.nextElementSibling;
        if (panel.style.maxHeight){
          panel.style.maxHeight = null;
        } else {
          panel.style.maxHeight = panel.scrollHeight + "px";
        }
      }
    }
    // ^^End accordions script

    $('#id_initial_interest').keyup(function () {
        // alert('');
        var amount_requested = parseInt($('#amount_requested').html());
        var initial_interest = parseInt($('#id_initial_interest').val());

        $('#id_amount_disbursed').val(amount_requested - initial_interest)
    });

    $(function () {
        $('#date_from').datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });
        $('#date_to' ).datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });

        /* -------General datepicker for any field that needs a datepicker!!----------------*/
        $('#date').datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });
    });

    $('#filters-form').submit(function () {

        if ( $('#date_from').val() == ''){

           $('#date_from').val('2000-01-01');
        }
        if ( $('#date_to').val() == ''){

           $('#date_to').val('2100-12-31');
        }
    });

//    Search member form

    $('form#search-member').submit(function () {

        $( "#search-results" ).html( "<span class='red'>Searching ...</span>" );

        var html = '';

        $.ajax({
            type: "POST",
            // dataType: 'json',
            url: $('form#search-member').attr('action'),
            data: $('form#search-member').serialize(),
            success: function (data) {
                var s_response = JSON.parse(data);

                if (s_response.success === 'true'){

                    $("#member_number").val(s_response.pk);

                    $("#member_number").attr('readonly', true);

                    // alert(new_input);


                    $('<input type="hidden" />').attr({
                        name: 'member_number',
                        value: s_response.pk
                    }).appendTo("form#guarantor-form");

                    html = "<h3>Request " + s_response.name + " to guarantee loan</h3>";

                }else{
                    alert(s_response.err);
                }

                $("#search-results").html(html);

            }
        });

        return false;
    });

    // submit request guarantor form
    $("form#guarantor-form").submit(function () {

        var data = $("form#guarantor-form").serialize();

        // alert(data);

        $.ajax({
            type: "POST",
            url: $('form#guarantor-form').attr('action'),
            data: data,
            success: function () {}
        });

        return true;
    });

});
