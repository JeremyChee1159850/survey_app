SET FOREIGN_KEY_CHECKS = 0;


truncate table plants;
truncate table users;


INSERT INTO `users` (id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status) VALUES
(101, 'siteadmin1', 'f8b0c38da5bcf5e7913b51e51a6e7e009c84110f377f0a0f1e178cd99e1bfe2a', 'siteadmin1@example.com', 'John', 'Doe', '{"lat": -45.9, "lon": 170.4}', NULL, 'default.png', 'siteadmin', 'active'),
(102, 'siteadmin2', '96bd7a2f308098c2e52d1cc3c9e5406f914f08fcf989989e35bc80c16063e455', 'siteadmin2@example.com', 'Jane', 'Smith', '{"lat": -45.0, "lon": 168.7}', NULL, 'default.png', 'siteadmin', 'active');


INSERT INTO `plants` (id, name, description, image, invasiveness) VALUES
-- For theme_id = 1 (surfing spot)
(1, 'Heather', 'Famous for its powerful waves and dramatic black sand beaches. A popular spot for surfers and photographers.', 'CallunaVulgaris.jpg', 'invasive'),
(2, 'Daphne', 'Known for its long left-hand break and relaxed atmosphere. Ideal for all levels of surfers.', 'daphne.jpg', 'non-invasive'),
(3, 'Pigs Ear', 'A rugged beach with consistent waves, suitable for experienced surfers. Also known for its gannet colony.', 'PigsEar.jpg', 'invasive'),
(4, 'Ice Plant', 'A picturesque spot with clear waters and great surf for beginners and intermediate surfers.', 'IcePlant.jpg', 'non-invasive'),
(5, 'Montbretia', 'A popular beach with great waves and a friendly surf community. Ideal for all skill levels.', 'montbretia.webp', 'invasive'),
(6, 'NZ Blueberry', 'A beautiful beach with consistent surf and a relaxed vibe. Perfect for a casual surf session.', 'blueberry.jpg', 'non-invasive'),
(7, 'Mexican Daisy', 'Located in Christchurch, it offers consistent surf and a great atmosphere for surfers.', 'daisy.jpg', 'invasive'),
(8, 'Kingfisher Daisy', 'Features powerful waves and excellent surf conditions. A great spot for advanced surfers.', 'KingfisherDaisy.jpg', 'non-invasive'),
(9, 'Aluminium Plant', 'Known for its fun and mellow waves, suitable for surfers of all levels.', 'AluminiumPlant.jpg', 'invasive'),
(10, 'Hosta Hybrid', 'Offers fantastic surf and stunning views. Popular among both locals and tourists.', 'hosta.jpg', 'non-invasive'),
(11, 'Tutsan', 'Located in the Bay of Islands, it provides good surf conditions and beautiful scenery.', 'tutsan.jpg', 'invasive'),
(12, 'Bush Lily', 'Renowned for its long, sandy beaches and great surf, ideal for longboarding.', 'BushLily.jpg', 'non-invasive'),
(13, 'Stinking Iris', 'A hidden gem with excellent surf and fewer crowds. Great for a more secluded surf experience.', 'StinkingIris.jpeg', 'invasive'),
(14, 'NZ Iris', 'Offers consistent surf and a vibrant surf community. A favorite among local surfers.', 'NZIris.webp', 'non-invasive'),
(15, 'Russell Lupin', 'Known for its scenic beauty and solid surf. Ideal for those looking to combine surfing with wildlife watching.', 'lupins.webp', 'invasive'),
(16, 'Koromiko', 'A stunning coastal location with great waves and a lighthouse backdrop. Perfect for advanced surfers.', 'koromiko.jpg', 'non-invasive'),
(17, 'Tradescantia', 'Features powerful surf and less crowded beaches. A great spot for experienced surfers.', 'Tradescantia.jpg', 'invasive'),
(18, 'Oxford Blue', 'Coromandel offers stunning scenery with ancient forests and peaks, plus great surf at Hot Water Beach', 'oxfordblue.jpg', 'non-invasive'),
(19, 'Periwinkle', 'Known for its beautiful beaches and great surf conditions. Ideal for surfers of all levels.', 'Periwinkle.jpg', 'invasive'),
(20, 'Creeping Pohuehue', 'Offers excellent surf and a laid-back vibe. Great for both beginners and experienced surfers.', 'pohuehue.jpg', 'non-invasive'),
(21, 'Bomarea', 'Famous for its powerful waves and dramatic black sand beaches. A popular spot for surfers and photographers.', 'Bomarea.jpg', 'invasive'),
(22, 'White Clematis', 'Known for its long left-hand break and relaxed atmosphere. Ideal for all levels of surfers.', 'clematis.jpg', 'non-invasive'),
(23, 'Clematis Vitalba', 'A rugged beach with consistent waves, suitable for experienced surfers. Also known for its gannet colony.', 'ClematisVitalba.jpg', 'invasive'),
(24, 'Clematis Henryii', 'A picturesque spot with clear waters and great surf for beginners and intermediate surfers.', 'henryii.webp', 'non-invasive'),
(25, 'English Ivy', 'A popular beach with great waves and a friendly surf community. Ideal for all skill levels.', 'englishivy.jpg', 'invasive'),
(26, 'Star Jasmine', 'A beautiful beach with consistent surf and a relaxed vibe. Perfect for a casual surf session.', 'starjasmine.jpg', 'non-invasive'),
(27, 'Japanese Honeysuckle', 'Located in Christchurch, it offers consistent surf and a great atmosphere for surfers.', 'japonica.jpg', 'invasive'),
(28, 'Sulphurea', 'Features powerful waves and excellent surf conditions. A great spot for advanced surfers.', 'sulphurea.jpg', 'non-invasive'),
(29, 'Flame Creeper', 'Known for its fun and mellow waves, suitable for surfers of all levels.', 'flamecreeper.jpeg', 'invasive'),
(30, 'Scarlet Rata', 'Offers fantastic surf and stunning views. Popular among both locals and tourists.', 'rata.webp', 'non-invasive');


SET FOREIGN_KEY_CHECKS = 1;