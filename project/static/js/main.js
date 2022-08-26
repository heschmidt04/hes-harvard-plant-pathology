import { Bar } from './bar.js';
import { Donut } from './donut.js';
import { Scatter } from './scatter.js';

(function(){
	console.log( 'hello world!' )
	d3.json( '/load_data' ) // async
		.then( data => main( data ) ) // run the application
		.catch( err => console.error( err ) ) // print errors if there are any
		
	
})();

// Global Variables
function main( data ) {
	// Input to main
	d3.select( "#users" )
		.append( "span" )
		.text( data.users.length )

	let	bars = new Bar( 'vis1', data );
	let donut = new Donut( 'vis2', data );
	let scatter = new Scatter( 'vis3', data );
}