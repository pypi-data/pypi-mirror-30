
/*global QUnit: true */
/*global setTimeout: true */
/*global start: true */

/*global $: true */

// ****************************************************************************
// Base
// ****************************************************************************

QUnit.module("Base");

// ----------------------------------------------------------------------------
// Left panel
// ----------------------------------------------------------------------------

QUnit.test("left panel, opened", function(assert) {
    assert.ok($('#leftClose').length, '<div id="leftClose"> exists');
    assert.ok($('#leftOpen').length, '<div id="leftOpen"> exists');
    assert.equal($('#content2').css('margin-left'), '0px',
                 'left margin of #content2 is 0px');
    assert.equal(Math.round($('#content2').offset().left),
                 Math.round($('#leftPanel').width() - $('#content1').width()),
                 'left of #content2 is width of left panel');
    assert.equal($('#leftPanel').css('display'), 'block', 'left panel is visible');
    assert.equal($('#leftPanel').offset().left, 0, 'left of left panel is 0');
}, 6);

QUnit.test("left panel, closed", function(assert) {
    var done = assert.async();
    $('#leftClose').click();
    setTimeout(function() {
        assert.equal(-$('#content2').offset().left, $('#content1').width(),
                     'right of #content2 is 100%');
        assert.equal($('#leftPanel').css('display'), 'none',
                     'left panel is not visible');
        assert.equal($('#rightPanel').offset().left, 0, 'left of right panel is 0');
        $('#leftOpen').click();
        done();
    }, 2000);
}, 3);

// ----------------------------------------------------------------------------
// Flash
// ----------------------------------------------------------------------------

QUnit.test("alert flash, visible", function(assert) {
    assert.equal($('#flash.alert').css('display'), 'block', 'flash is visible');
}, 1);

// ----------------------------------------------------------------------------
// Tab set
// ----------------------------------------------------------------------------

QUnit.test("tab set, tab n°0", function(assert) {
    $('#tab0').click();
    assert.equal($('.tabCurrent a').attr('id'), 'tab0', 'tab0 is selected');
    assert.equal($('#tabContent0').css('display'), 'block', 'tabContent0 is visible');
    assert.equal($('#tabContent1').css('display'), 'none',
                 'tabContent1 is not visible');
}, 3);

QUnit.test("tab set, tab n°1", function(assert) {
    var done = assert.async();
    $('#tab1').click();
    setTimeout(function() {
        assert.equal($('.tabCurrent a').attr('id'), 'tab1', 'tab1 is selected');
        assert.equal($('#tabContent0').css('display'), 'none',
                     'tabContent0 is not visible');
        assert.equal($('#tabContent1').css('display'), 'block',
                     'tabContent1 is visible');
        $('#tab0').click();
        done();
    }, 1000);
}, 3);

// ----------------------------------------------------------------------------
// Tool tip
// ----------------------------------------------------------------------------

QUnit.test("tool tip, show", function(assert) {
    $('#tooltip1').mouseenter();
    assert.ok($('#toolTipContent').length,
              '<div id="toolTipContent"> has appeared');
    $('#tooltip1').mouseleave();
    assert.equal($('#toolTipContent').length, 0,
                 '<div id="toolTipContent"> has disappeared');
}, 2);

// ----------------------------------------------------------------------------
// Buttons
// ----------------------------------------------------------------------------

QUnit.test("buttons, check all", function(assert) {
    $('#check_all').click();
    assert.equal($('.listCheck:checked').length, 2, 'All buttons are checked');
    $('#check_all').click();
    assert.equal($('.listCheck:checked').length, 0, 'All buttons are unchecked');
}, 2);

QUnit.test("buttons, slow", function(assert) {
    $('#up').click();
    assert.equal($('#up img').attr('src'), '/Static/Images/wait_slow.gif',
                 'Slow state');
}, 1);
