// generate-photo-album.js
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const imageDir = path.join(__dirname, "public", "images");
const outputFile = path.join(__dirname, "src", "gallery", "PhotoGallery.jsx");

async function getImageMetadata(filePath) {
  try {
    const metadata = await sharp(filePath).metadata();
    return {
      width: metadata.width,
      height: metadata.height,
    };
  } catch (err) {
    console.error(`Error reading ${filePath}:`, err);
    return null;
  }
}

async function generateGallery() {
  const files = fs.readdirSync(imageDir).filter(file =>
    /\.(jpe?g|png|webp)$/i.test(file)
  );

  const photos = [];

  for (const file of files) {
    const fullPath = path.join(imageDir, file);
    const dimensions = await getImageMetadata(fullPath);

    if (dimensions) {
      photos.push({
        src: `/images/${file}`,
        width: dimensions.width,
        height: dimensions.height,
      });
    }
  }

  const componentContent = `
import React from "react";
import PhotoAlbum from "react-photo-album";
import { RowsPhotoAlbum } from "react-photo-album";

const photos = ${JSON.stringify(photos, null, 2)};

function PhotoGallery() {
  return (
    <div>
      <h1>Scenes from Terra</h1>
      <RowsPhotoAlbum photos={photos} />
    </div>
  );
}

export default PhotoGallery;
  `.trim();

  fs.writeFileSync(outputFile, componentContent);
  console.log(`PhotoGallery.jsx generated with ${photos.length} images.`);
}

generateGallery();
