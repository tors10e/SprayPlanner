import React from "react";
import trail_map from '../images/on_property_trails.jpg';


const Trails = () => {
    return (
        <div className="section-heading">
            <h2 id="trails">Trails</h2>
            <p>Get out and enjoy these beautiful mountains. We have a few trails that make for easy walking or spend
                some
                time walking
                through the vineyard. We have two basic loops that are fit for general use, the Eastern Creek Loop
                and
                the Spring House Loop.</p>
            <p>The creek trail starts at the pavilion and works its way down to Falls Branch and follows
                it up to the gravel road. Visitors can then follow the road back to the start or contour along the
                bottom of the vineyard and back up. On the Western hillside, the Spring House loop takes you along
                the
                edge of our hybrid grapes and then to an old dry-stack, spring house.
            </p>
            <p>
                Although you can spend some time hiking at Terra, you can also use us as a base-of-operations and
                explore
                other nearby
                hiking and mountain biking trails. Have a look at this list on
                <a href="https://www.alltrails.com/lists/near-terra" target="_blank"> AllTrails Near Terra</a> for
                better information
            </p>
                <h4>
                    <a href={trail_map} target="_blank" className="btn btn-primary">Click here to
                        see the trail map</a>
                </h4>
        </div>
        );
    };

export default Trails;