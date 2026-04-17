import PhotoAlbum from "react-photo-album";
import "react-photo-album/styles.css";
import TerraNavbar from "../components/navbar";
import Header from "../components/header";
import Lightbox from "yet-another-react-lightbox";
import "yet-another-react-lightbox/styles.css";

// import optional lightbox plugins
import Fullscreen from "yet-another-react-lightbox/plugins/fullscreen";
import Slideshow from "yet-another-react-lightbox/plugins/slideshow";
import Thumbnails from "yet-another-react-lightbox/plugins/thumbnails";
import Zoom from "yet-another-react-lightbox/plugins/zoom";
import "yet-another-react-lightbox/plugins/thumbnails.css";

import getPhotoList from "./PhotoList";
import React, { useState } from 'react';

export function PhotoGallery() {
    const [index, setIndex] = useState(-1);
    const photos = getPhotoList();

    return (
        <> 
        <Header/>
        <TerraNavbar/>    
        <h1>Terra Photo Gallery</h1>
            <PhotoAlbum
            layout="columns"
            photos={photos} 
            spacing={10}
            // targetRowHeight={300}
            onClick={({ index }) => setIndex(index)}
            />
            <Lightbox
                index={index}
                slides={photos}
                open={index >= 0}
                close={() => setIndex(-1)}
                plugins={[Fullscreen, Slideshow, Thumbnails, Zoom]}
            />
        </>
        );
}
