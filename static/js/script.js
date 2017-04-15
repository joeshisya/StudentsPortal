$('#canvas').click(function()
{
    $('#canvas').hide();
});

var $scoreGroup = $('#scoreGroup');
$scoreGroup.on('hidden.bs.collapse', function()
{
	$scoreGroup.find('.collapse.in').collapse('hide');
});

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
