export class Base {
	// data
	data_bins = [];

	// Elements
	svg = null;
	g = null;

	// Configs
	svgW = 360;
	svgH = 360;
	gMargin = { top: 50, right: 50, bottom: 50, left: 50 };
	gW = this.svgW - ( this.gMargin.right + this.gMargin.left );
	gH = this.svgH - ( this.gMargin.top + this.gMargin.bottom );

	axes = {
		x : {
			link : d3.axisBottom(),
			scale : [],
			offset : 0,
			group : null,
		},
		y : {
			link : d3.axisLeft(),
			scale : [],
			offset : 0,
			group : null,
		},
	};

	// d3
	histogram = null;
	scX = null;
	scY = null;
	axisXG = null;
	axisYG = null;
	
	constructor( _target, _data ) {
		// Assign parameters as object fields
		this.data = _data.users;
		this.target = _target;
		this.parent = null;
		this.tooltip = null;

		// Need a random id, in case we have multple donuts on one page
		let randomVal = Math.floor( Math.random() * 1024 );
		this.id = this.constructor.name + "_" + randomVal.toString( 16 ).toUpperCase();

		// Now init
		if( this.constructor === Base ) this.init();
	}
	
	init() {
		// Define this vis
		const vis = this;
		console.log( vis.target )

		// target div
		vis.parent = d3.select( `#${vis.target}` );

		// Set up the svg/g workspace
		vis.svg = vis.parent
			.append('svg')
			.attr( 'id', vis.id )
			.attr( 'width', vis.svgW )
			.attr( 'height', vis.svgH );
		vis.g = vis.svg.append( 'g' )
			.attr('class', 'container')
		   // .style('transform', `translate(${vis.gMargin.left}px, ${vis.gMargin.top}px)`);

		// Now wrangle
		if( this.constructor === Base ) vis.wrangle();
	}
	
	wrangle() {
		// Define this vis
		const vis = this;

		// Now render
		vis.render();
	}
	
	render() {
		// Define this vis
		const vis = this;
	}
}
export default Base;
