import $ from 'jquery';

var context = require.context( './app/assets/', true, /-spec\.js$/ );

context.keys().forEach( context );
