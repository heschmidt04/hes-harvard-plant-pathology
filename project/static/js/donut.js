import { Base } from "./base.js"

export class Donut extends Base {
	constructor( _target, _data ) {
		super( _target, _data );

		// create space for the color scheme
		this.color = null;

		// create space for the pie
		this.pie = d3.pie();

		// the arc generator
		this.arc = d3.arc();

		// Need a random id, in case we have multple donuts on one page
		let randomVal = Math.floor( Math.random() * 1024 );
		this.id = "donut_" + randomVal.toString( 16 ).toUpperCase();

		this.init();
	}

	init() {
		// Define this vis
		const vis = this;

		super.init();

		// Shift the origin
		let offset = {
			x : Math.floor( vis.svgW / 2.0 ),
			y : Math.floor( vis.svgH / 2.0 ),
		};
		vis.g.style('transform', `translate(${ offset.x }px, ${ offset.y }px)`);

		// The label
		vis.g.append( 'text' )
			.attr( 'class', 'label' )
			.attr( 'text-anchor', 'middle' )
			.attr( 'dy', -( offset.y * .8 ) )
			.text( "Programming Languages" )

		// set the color scale to something pleasant
		vis.color = d3.scaleOrdinal().range( d3.schemeYlGn[9] )

		// set the pie's data binder
		vis.pie.value( d => d.value );

		// set the size of each arc
		let oR = Math.floor( vis.gW / 2.0 ); // The outer radius = to the drawable svg - the margin
		let iR = Math.floor( vis.gH / 4.0 ); // inner radius is half of outer radius, giving a ring diameter of 1/4
		vis.arc.innerRadius( iR ).outerRadius( oR );

		// Create the group where the numbers will reside
		vis.g.append( 'g' ).attr( 'id', vis.id + "_detail" );

		vis.wrangle();
	}

	wrangle() {
		const vis = this;

		// let's use d3.nest() to create a categorical histogram
		// vis.histogram = d3.nest()
		// 	.key( d => d.prog_lang )             // looking at languages
		// 	.rollup( d => d3.sum( d, g => 1 ) )  // we want to count each one
		// 	.entries( vis.data )                 // taking entries from the data
			
		// let's use d3.nest() to create a categorical histogram
		// let hist = d3.group( vis.data, d => d.prog_lang ) // looking at languages
		// console.log( hist )
		vis.histogram = d3.rollups( vis.data, v => v.length, d => d.prog_lang )  // we want to count each one
	
		let domain = [
			d3.min( vis.histogram.values() ) - 1,
			d3.max( vis.histogram.values() ) + 1,
		];
		vis.color.domain( domain );

		vis.render();
	}

	render() {
		const vis = this;
		
		// Get the arcs
		let arcs = vis.pie( vis.histogram.map( d => { return { key: d[0], value: d[1] }; } ) )

		// Set up the segment groups
		const segment = vis.g.selectAll( '.segment' )
			.data( arcs )
			.enter()
			.append( 'g' )
			.attr( 'class', 'segment' );
			

		// Set up the actual arc path
		const path = segment.append( 'path' )
			.attr( 'id', ( d, i ) => vis.id + "_arc_" + d.index )
			.attr( 'fill', ( d, i ) => vis.color( i ) )
			.attr( 'f0', ( d, i ) => vis.color( i ) )
			.attr( 'd', vis.arc )
			.on( 'mouseover', vis.handleMouseOver.bind( vis ) ) // we're binding these because we need
			.on( 'mouseout', vis.handleMouseOut.bind( vis ) )   // some state! Should prob add to lab info.
			// HW: Animate the arc to draw over time (~750ms)


		// Set up the text label
		const text = segment.append( "text" )
			.attr( 'id', ( d, i ) => vis.id + "_label_" + d.index )
			.attr( 'transform', d => `translate(${vis.arc.centroid(d)})` )
			.text( d => d.data.key )
			.attr( 'fill', 'white' )
			.attr( 'text-anchor', 'middle' );
	}

	static _getLabel( id, index ) {
		console.log( id, index )
		return document.getElementById( id + "_label_" + index );
	}

	static _getArc( id, index ) {
		return document.getElementById( id + "_arc_" + index );
	}

	handleMouseOver( e, d, i ) {
		// Append detail text
		let me = d3.select( "#" + this.id + "_detail" )
			.append( 'text' )
			.attr( 'class', 'result resultD' )
			.attr("text-anchor", "middle" )
			.attr( 'y', function( d, i ) {
				// here, we offset the number by half the height, so it's actually
				// centered (or pretty close to it)
				return getComputedStyle( this )
					.getPropertyValue( 'font-size' )
					.split("px")[0] / 2 + "px";
			})
			.text( d.value )
			
		
		
		// Set the .hover class
		let label = d3.select( `#${this.id}_label_${d.index}` )
		   label.classed( "hover", !label.classed( "hover" )  );
		
		// Plain JS way
		//let label = Donut._getLabel( this.id, d.index ).classList.add( 'hover' );

		let arc = Donut._getArc( this.id, d.index );
		arc.classList.add( 'hover' )
		d3.select( "#" + arc.id )
			.transition()
			.duration(1000)
			.attr( 'fill', 'darkorange' );
	}

	handleMouseOut( e, d, i ) {		
		// remove the text
	   d3.selectAll( "#" + this.id + "_detail > * ").remove()
	   
	   // un-hover the label
	   let label = d3.select( `#${this.id}_label_${d.index}` )
	   label.classed( "hover", !label.classed( "hover" ) );
	   
	   // Plain JS way
	   //let label = Donut._getLabel( this.id, d.index ).classList.remove( 'hover' );

		// get the html arc
		let arc = Donut._getArc( this.id, d.index )
		// remove the class
		arc.classList.remove( 'hover' )
		// get the d3 arc
		arc = d3.select( "#" + arc.id );
		arc.transition()
			.duration(200)
			.attr( 'fill', arc.attr( 'f0' ) );
	}
}
export default Donut;
