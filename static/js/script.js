var $scoreGroup = $('#scoreGroup');
$scoreGroup.on('hidden.bs.collapse', function()
{
	$scoreGroup.find('.collapse.in').collapse('hide');
});

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
            $('form#BOOK').submit();
        }
    }
);

$('#important_notify_info').click(function()
    {
        alert("CLICKED")
    }
);

/*
$(document).ready(function()
{
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    context.beginPath();
    context.fillStyle = "yellow";
    context.strokeStyle = "black";
    context.font = "20px Georgia";
    context.linewidth = 10;
    context.arc(100, 100, 75, 0, 2 * Math.PI, false);
    context.fill();
    context.beginPath()
    context.fillStyle = "red";
    context.fillText("Hello World", 40, 100);
    context.fill();
});
*/