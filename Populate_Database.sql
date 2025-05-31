SET FOREIGN_KEY_CHECKS = 0;


truncate table plants;
truncate table users;


INSERT INTO `users` (id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status) VALUES
(101, 'siteadmin1', 'f8b0c38da5bcf5e7913b51e51a6e7e009c84110f377f0a0f1e178cd99e1bfe2a', 'siteadmin1@example.com', 'John', 'Doe', '{"lat": -45.9, "lon": 170.4}', NULL, 'default.png', 'siteadmin', 'active'),
(102, 'siteadmin2', '96bd7a2f308098c2e52d1cc3c9e5406f914f08fcf989989e35bc80c16063e455', 'siteadmin2@example.com', 'Jane', 'Smith', '{"lat": -45.0, "lon": 168.7}', NULL, 'default.png', 'siteadmin', 'active');


INSERT INTO `plants` (id, name, description, image, invasiveness) VALUES
-- For theme_id = 1 (surfing spot)
(1, 'Heather', 'A small evergreen shrub with pinkish-purple flowers.', 'CallunaVulgaris.jpg', 'invasive'),
(2, 'Daphne', 'A fragrant shrub with clusters of pale pink or white flowers.', 'daphne.jpg', 'non-invasive'),
(3, 'Pigs Ear', 'A succulent with thick, fleshy leaves and pinkish flowers.', 'PigsEar.jpg', 'invasive'),
(4, 'Ice Plant', 'A hardy ground cover with vibrant flowers and moisture-retaining leaves.', 'IcePlant.jpg', 'non-invasive'),
(5, 'Montbretia', 'A flowering plant with sword-like leaves and bright orange-red blooms.', 'montbretia.webp', 'invasive'),
(6, 'NZ Blueberry', 'A native shrub producing edible berries and small white flowers.', 'blueberry.jpg', 'non-invasive'),
(7, 'Mexican Daisy', 'A daisy-like plant with small white flowers.', 'daisy.jpg', 'invasive'),
(8, 'Kingfisher Daisy', 'A low-maintenance plant with blue-purple blooms.', 'KingfisherDaisy.jpg', 'non-invasive'),
(9, 'Aluminium Plant', 'Recognised by its silver-striped leaves.', 'AluminiumPlant.jpg', 'invasive'),
(10, 'Hosta Hybrid', 'A shade-loving perennial with broad green leaves and lilac flowers.', 'hosta.jpg', 'non-invasive'),
(11, 'Tutsan', 'A shrub with yellow flowers and red berries.', 'tutsan.jpg', 'invasive'),
(12, 'Bush Lily', 'An attractive plant with large, orange-red flowers.', 'BushLily.jpg', 'non-invasive'),
(13, 'Stinking Iris', 'Produces striking purple flowers and orange seeds.', 'StinkingIris.jpeg', 'invasive'),
(14, 'NZ Iris', 'A native iris with pale blue flowers and grassy leaves.', 'NZIris.webp', 'non-invasive'),
(15, 'Russell Lupin', 'Produces bright yellow flowers.', 'lupins.webp', 'invasive'),
(16, 'Koromiko', 'A tall plant with colourful flower spikes.', 'koromiko.jpg', 'non-invasive'),
(17, 'Tradescantia', 'A native shrub with white to purple flower spikes.', 'Tradescantia.jpg', 'invasive'),
(18, 'Oxford Blue', 'Also known as wandering willie, it spreads quickly and smothers ground-level vegetation.', 'oxfordblue.jpg', 'non-invasive'),
(19, 'Periwinkle', 'Features silver-blue foliage and deep purple flowers.', 'Periwinkle.jpg', 'invasive'),
(20, 'Creeping Pohuehue', 'Sprawling groundcover with violet flowers.', 'pohuehue.jpg', 'non-invasive'),
(21, 'Bomarea', 'A native vine with small white flowers and dark green leaves.', 'Bomarea.jpg', 'invasive'),
(22, 'White Clematis', 'A climbing plant with colourful, trumpet-shaped flowers.', 'clematis.jpg', 'non-invasive'),
(23, 'Clematis Vitalba', 'A vigorous climber with showy white flowers.', 'ClematisVitalba.jpg', 'invasive'),
(24, 'Clematis Henryii', 'A fast-growing vine that smothers trees and shrubs.', 'henryii.webp', 'non-invasive'),
(25, 'English Ivy', 'An ornamental clematis with large white blooms.', 'englishivy.jpg', 'invasive'),
(26, 'Star Jasmine', 'A well-known climbing vine that clings to walls and trees.', 'starjasmine.jpg', 'non-invasive'),
(27, 'Japanese Honeysuckle', 'A fragrant climber with glossy leaves and white star-shaped flowers.', 'japonica.jpg', 'invasive'),
(28, 'Sulphurea', 'A woody vine with fragrant flowers.', 'sulphurea.jpg', 'non-invasive'),
(29, 'Flame Creeper', 'An aggressive vine with vibrant red-orange flowers.', 'flamecreeper.jpeg', 'invasive'),
(30, 'Scarlet Rata', 'A native climber with bright red flowers.', 'rata.webp', 'non-invasive');


SET FOREIGN_KEY_CHECKS = 1;