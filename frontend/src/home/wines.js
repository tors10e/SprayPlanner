import React from "react";
import Bsmodal from '../components/bsmodal';
import Image from 'react-bootstrap/Image'
import cab_label from '../images/bottle_labels/cab_sav_214x300.jpg';
import cardinal_label from '../images/bottle_labels/cardinal_214x300.jpg';
import celestial_label from '../images/bottle_labels/celestial_214x300.jpg';
import compass_label from '../images/bottle_labels/compass_214x300.jpg';
import triangulation_label from '../images/bottle_labels/triangulation_214x300.jpg';
import true_north_label from '../images/bottle_labels/true_north_214x300.jpg';
import meridian_label from '../images/bottle_labels/meridian_214x300.jpg';


function Wines(props) {
    return(
            <div class="topic topic-even section-heading">
                <h2 id="wines">Wines</h2>
                <p>We have a wide variety of wines from dry Cabernet Sauvignon to sweet berry wines so that we have something for everyone. </p>
                    <div class="row">
        <Bsmodal
            image_src={triangulation_label}
            button_text="Click for more information"
            title_text="Triangulation"
            body_text="Notes of plum, black cherry and tobacco meld to create a medium body and lightly oaked red wine that's perfect for settling into a relaxing evening."
         />
        <Bsmodal
            image_src={cab_label}
            button_text="Click for more information"
            title_text="Cabernet Sauvignon"
            body_text="Notes of plum, black cherry and tobacco meld to create a medium body and lightly oaked red wine that's perfect for settling into a relaxing evening. 13% abv, 750 ml"
         />
        <Bsmodal
            image_src={cardinal_label}
            button_text="Click for more information"
            title_text="Cardinal Direction"
            body_text="A unique blend of Cabernet Sauvignon, Chambourcin, Merlot, and a splash of Chardonnay creates an easy drinking favorite with a fruit forward nose. 12% abv., 750 ml."
         />
        <Bsmodal
        image_src={compass_label}
            button_text="Compass Rose"
            title_text="Compass Rose"
            body_text="Medium dry blend of Pinot Grigio and Chambourcin creates flavors of green apple and strawberry. 12% abv, 750 ml"
         />
         <Bsmodal
            image_src={meridian_label}
            button_text="White Meridian"
            title_text="White Meridian"
            body_text="A classic bold Muscadine with sweetness that balances it's crisp acidity. A southern favorite. 12% abv, 750 ml"
         />
        <Bsmodal
            image_src={true_north_label}
            button_text="True North"
            title_text="True North"
            body_text="A blend of Vidal Blanc, Chardonnay, and Pinot Grigio. Crisp apple on the palate with a lemony finish and just a hint of peach and grapefruit."
         />
        <Bsmodal
            image_src={celestial_label}
            button_text="Celestial Spheres"
            title_text="Celestial Spheres"
            body_text="This sparkling muscadine has a carbonated twist to it that makes it great for celebrating a special occasion or a great weekend with friends and family. 12% abv, 750 ml"
         />
         </div>
</div>

    );
};

export default Wines;