import React from "react";
import {WinterHours} from './hours_winter';
import {SummerHours} from './hours_summer';

const Hours = () => {
    return (
        <div className="topic topic-even section-heading">
            <h2 id="hours">Operating Hours and Seasons</h2>
            <div className="container">
                <WinterHours />
                <SummerHours />
                <p class="text-muted p-3 small">* <em>Special events are available by appointment</em></p>
            </div>
        </div>
    );
};

        export default Hours;