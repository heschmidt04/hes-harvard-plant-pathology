import { Base } from "./base.js"

export class Scatter extends Base {
	constructor( _target, _data ) {
		super( _target, _data );

		this.hours_bins = null;
		this.experience_bins = null;

		this.init();
	}

	init() {
		// Define this vis
		const vis = this;

		super.init();

		this.tooltip = this.parent.append( 'div' )
			.attr( 'id', this.id + "_tooltip" )
			.attr( 'class', 'tooltip' )
			.style( "opacity", 0 )
			.append( 'p' )

		// center the graph
		vis.g.style('transform', `translate(${vis.gMargin.left}px, ${vis.gMargin.top - 15}px)`)

		// set the scale
		this.axes.x.scale = [ 0, d3.max( this.data, d => d.experience_yr ) ];
		this.axes.x.link = d3.scaleLinear()
			.domain( this.axes.x.scale )
			.range( [ 0, this.gW ] );

		this.axes.y.scale = [ 0, d3.max( this.data, d => d.hw1_hrs ) ];
		this.axes.y.link = d3.scaleLinear()
			.domain( this.axes.y.scale )
			.range( [ this.gH, 0 ] );
		
		vis.histogram = d3.histogram();

		vis.wrangle();
	}

	wrangle() {
		const vis = this;

		// lets figure out how variable the hours are
		vis.hours_bins = d3.rollups( vis.data, v => v.length, d => d.hw1_hrs )

		// lets figure out how variable the experiences are
		vis.experience_bins = d3.rollups( vis.data, v => v.length, d => d.experience_yr )

		this.render();
	}
	
	// v4,5 method
	// wrangle() {
	// 	// let's use d3.nest() to figure out how many different ages there are
	// 	this.hours_bins = d3.nest()
	// 		.key( d => d.hw1_hrs )                   // looking at ages
	// 		.rollup( d => d3.sum( d, g => 1 ) )  // we want to count each one
	// 		.entries( vis.data )                    // taking entries from the data
	// 		
	// 	// v4,5 method
	// 	this.experience_bins = d3.nest()
	// 		.key( d => d.experience_yr )         // looking at experience
	// 		.rollup( d => d3.sum( d, g => 1 ) )  // we want to count each one
	// 		.entries( vis.data )                    // taking entries from the data
	// }

	render() {
		const vis = this;

		let step = {
			x : vis.gW / vis.experience_bins.length,
			y : vis.gH / vis.hours_bins.length
		};

		// Draw the axes
		let x_axis = this.g.append( 'g' )
			.attr( 'transform', `translate(${(vis.gMargin.left - step.x) }, ${ vis.gH + step.y })`)
			.attr("foo", "bar")
			.call( d3.axisBottom( vis.axes.x.link ) );
		
		x_axis.append( 'text' )
			.text( "Years of Experience" )
			.attr( 'class', 'label' )
			.attr( 'text-anchor', 'middle' )
			.attr( 'x', vis.gW / 2 )
			.attr( 'dy', '2.5em' )

		let y_axis = this.g.append( 'g' )
			.attr( 'transform', `translate(${vis.gMargin.left - ( step.x * 2 ) }, 0)`)
			.call( d3.axisLeft( vis.axes.y.link ) );
		
		y_axis.append( 'text' )
			.text( 'Homework Hours' )
			.attr( 'class', 'label' )
			.attr( 'text-anchor', 'middle' )
			.attr( 'transform', 'rotate(-90)' )
			.attr( 'x', -( vis.gH / 2 ) )
			.attr( 'y', -vis.gMargin.left  )
			.attr( 'dy', "1em" )


		// draw the data
		let dots = this.g.append( 'g' )
			.attr( 'transform', `translate(${vis.gMargin.left - step.x }, ${vis.gH / vis.hours_bins.length - step.y })`)
			.selectAll( "circle" )
			.data( vis.data )
			.enter()
			.append( "circle" )
			.attr( 'id', ( d, i ) => this.id + "_dot_" + i )
			.attr( "cx", d => vis.axes.x.link( d.experience_yr ) )
			.attr( "cy", d => vis.axes.y.link( d.hw1_hrs ) )
			.attr( 'r0', d => d.age / vis.axes.x.scale[ 1 ] )
			.style( 'fill', "#69b3a2" )
			.attr( 'f0', "#69b3a2" )
			.on( 'mouseover', vis.handleMouseOver )
			.on( 'mouseout', vis.handleMouseOut )
			.transition()
				.delay( 1000 )
				.duration(750)
				.attr( "r", d => d.age / vis.axes.x.scale[ 1 ] ) // normalize the age between [0,max] => [0,1]

	}

	static _getTooltip( id ) {
		let segs = id.split( "_dot_" )
		let elem_id = [ "#", segs[ 0 ], "_tooltip" ].join('')
		return d3.select( elem_id );
	}

	handleMouseOver( e, d, i ) {
// 
// 		console.log( this )
// 		console.log( d )
// 		console.log( i )
		// console.log( e )

		let dot = d3.select( "#" + this.id )
		dot.transition()
			.duration(200)
			.style( 'fill', 'darkorange' )
			.attr( 'r', 10 )

		let tooltip = Scatter._getTooltip( this.id )
			.style( 'position', 'absolute' )
			.style( 'left', `${e.pageX + 15}px` )
			.style( 'top', `${e.pageY -15}px` )			
			.transition()
			.duration(200)
			.style( 'opacity', .9 )

		tooltip.select( 'p' )
			.text( [ d.first_name, '(', d.age, ')'].join( ' ' ) )
	}

	handleMouseOut( e, d, i ) {
		let dot = d3.select( "#" + this.id )
		dot.transition()
			.duration(200)
			.style( 'fill', dot.attr( 'f0' ) )
			.attr( 'r', dot.attr( 'r0' ) )

		let tooltip = Scatter._getTooltip( this.id )
		tooltip.transition()
			.duration(200)
			.style( 'opacity', 0 )
	}
}
export default Scatter;
