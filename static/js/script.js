$('#paragraph').click(function()
{
    $('#paragraph').hide();
});

var $scoreGroup = $('#scoreGroup');
$scoreGroup.on('hidden.bs.collapse', function()
{
	$scoreGroup.find('.collapse.in').collapse('hide');
});
