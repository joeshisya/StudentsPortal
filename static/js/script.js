$(document).ready(function()
    {
        $('#toggle').click(function()
        {
            $('#sidebar').animate(
                {
                    width: "toggle"
                },
                250,
                function(){/* Run after animation completes */}
            )
        });

        $('#search').click(function()
            {
                alert("Search Functionality To be Implemented");
                return false;
            }
        );

        $('#hostel-submit').click(function()
            {
                if(confirm("Click ok to continue"))
                {
                    $('form#BOOK').submit();        }
                else
                {
                    return false;
                }
            }
        );

        function confirm_feature_test_fields()
        {
            var client = $('#client').val();
            var message = $('#message_body').val();
            var button = $('#feature_test_button');

            if(client == null || message == "")
            {
                button.attr('disabled', 'disabled');
            }
            else
            {
                button.removeAttr('disabled')
            }
        }

        $('#client').change(function()
            {
                confirm_feature_test_fields()
            }
        );


        $('#message_body').change(function()
            {
                confirm_feature_test_fields()
            }
        );

        $('#important_notify_info').click(function()
            {
                alert("CLICKED")
            }
        );
    }
);