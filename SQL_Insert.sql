-- USE LLCMS;
/*Ensure that you have enough data so that you can test and demonstrate the system, e.g. we would expect
to see at least 20 members, 5 tutors and 2 managers as a minimum, at least 20 scheduled workshops, 20
scheduled lessons, 20 membership payments, 10 payments and bookings for lessons and 10 bookings and
payments for workshops. */

#delete from users;
#delete from member;

/* Userrole
	MM - Member (20pax)
    TT - Tutor (5pax)
    MG - Manager (2pax)*/

INSERT INTO user VALUES
(1, 'member1', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(2, 'member2', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(3, 'member3', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(4, 'member4', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(5, 'member5', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(6, 'member6', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(7, 'member7', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(8, 'member8', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(9, 'member9', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(10, 'member10', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(11, 'member11', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(12, 'member12', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(13, 'member13', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(14, 'member14', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(15, 'member15', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(16, 'member16', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(17, 'member17', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(18, 'member18', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(19, 'member19', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(20, 'member20', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MM', 'A'),
(21, 'tutor1', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'TT', 'A'),
(22, 'tutor2', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'TT', 'A'),
(23, 'tutor3', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'TT', 'A'),
(24, 'tutor4', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'TT', 'A'),
(25, 'tutor5', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'TT', 'A'),
(26, 'manager1', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MG', 'A'),
(27, 'manager2', '0c3733e865e4b36e2fd1b95bb9c471126d6b2c5624c8f0e0cdc510af987788ef', 'MG', 'A');

INSERT INTO member VALUES
(1, 'Mr', 'Deandre', 'Simmons', NULL,'021-555522','deandre@gmail.com','','1980-02-01', NULL, NULL, NULL),
(2, 'Mr', 'Zara', 'Donovan', NULL,'021-554422','zara@gmail.com','','1981-05-01', NULL, NULL, NULL),
(3, 'Mrs', 'Allie', 'Newman', NULL,'021-588522','allie@gmail.com','','1982-03-01', NULL, NULL, NULL),
(4, 'Mr', 'Jeremy', 'Nichols', NULL,'021-235522','jeremy@gmail.com','','1984-05-01', NULL, NULL, NULL),
(5, 'Ms', 'Priscilla', 'Bryan', NULL,'021-575522','priscilla@gmail.com','','1988-03-01', NULL, NULL, NULL),
(6, 'Ms', 'Jalen', 'Fleming', NULL,'021-555342','jalen@gmail.com','','1981-06-01', NULL, NULL, NULL),
(7, 'Mr', 'Mohamed', 'Phelps', NULL,'021-552322','mohamed@gmail.com','','1980-03-01', NULL, NULL, NULL),
(8, 'Mr', 'Clark', 'Solomon', NULL,'021-556522','clark@gmail.com','','1989-06-01', NULL, NULL, NULL),
(9, 'Mr', 'Luke', 'Terrell', NULL,'021-5524522','luke@gmail.com','','1987-09-24', NULL, NULL, NULL),
(10, 'Mr', 'Brooke', 'Good', NULL,'021-553422','brooke@gmail.com','','1984-07-01', NULL, NULL, NULL),
(11, 'Mr', 'Christian', 'Burns', NULL,'021-555522','christian@gmail.com','','1980-02-01', NULL, NULL, NULL),
(12, 'Mr', 'Erik', 'Ray', NULL,'021-554422','erik@gmail.com','','1981-05-01', NULL, NULL, NULL),
(13, 'Mrs', 'Lina', 'Moore', NULL,'021-588522','line@gmail.com','','1982-03-01', NULL, NULL, NULL),
(14, 'Mr', 'Collin', 'Hinton', NULL,'021-235522','collin@gmail.com','','1984-05-01', NULL, NULL, NULL),
(15, 'Ms', 'Karen', 'Montgomery', NULL,'021-575522','karen@gmail.com','','1988-03-01', NULL, NULL, NULL),
(16, 'Ms', 'Holly', 'Whitney', NULL,'021-555342','holly@gmail.com','','1981-06-01', NULL, NULL, NULL),
(17, 'Mr', 'Tyler', 'Gross', NULL,'021-552322','tyler@gmail.com','','1980-03-01', NULL, NULL, NULL),
(18, 'Mr', 'Jade', 'Gibson', NULL,'021-556522','jade@gmail.com','','1989-06-01', NULL, NULL, NULL),
(19, 'Mr', 'Drew', 'Barnett', NULL,'021-5524522','drew@gmail.com','','1987-09-24', NULL, NULL, NULL),
(20, 'Mr', 'Andi', 'Evans', NULL,'021-553422','andi@gmail.com','','1984-07-01', NULL, NULL, NULL);

INSERT INTO staff VALUES
(21, 'Mr','Christopher', 'Stanley', NULL, '021-555522', 'christopher@jones.com', NULL),
(22, 'Mr','Pedro', 'Long', NULL, '021-555522', 'pedro@jones.com', NULL),
(23, 'Mrs','Adelynn', 'Ball', NULL, '021-555522', 'adelynn@jones.com', NULL),
(24, 'Ms','Grey', 'Kim', NULL, '021-555522', 'grey@jones.com', NULL),
(25, 'Mr','Spencer', 'Pittman', NULL, '021-555522', 'spencer@jones.com', NULL),
(26, 'Mr','Reid', 'Osborne', 'Manager', '021-555522', 'reid@jones.com', NULL),
(27, 'Mr','Noah', 'Jefferson', 'Manager', '021-555522', 'noah@jones.com', NULL);

INSERT INTO workshop_info VALUES
(1, 'Animal Teeth Care', 'Discover the secrets to keeping your pets'' teeth healthy and strong with our Animal Teeth Care workshop. Our experts will share valuable tips and techniques for proper dental care.'),
(2, 'Animal Feet Care', 'Join us for an interactive session focused on Animal Feet Care, where you''ll learn how to inspect your pet''s paws, recognize potential issues, and implement preventive measures.'),
(3, 'Field Trips', 'Explore the world outside the classroom walls with our Field Trips workshop. Learn about different types of excursions, safety protocols, and ways to integrate real-world experiences into your curriculum.'),
(4, 'Legal Requirements', 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.'),
(5, 'Breeding', 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.'),
(6, 'Genetics', 'Calling all science enthusiasts! Don''t miss our workshop dedicated to Genetics. Discover how genes influence traits, diseases, and evolutionary processes, and how genetic technologies shape our understanding of life.'),
(7, 'Crops', 'Dive into the art and science of crop production with our workshop. Gain insights into soil management, crop rotation, pest and disease control, and other key aspects of successful crop cultivation.'),
(8, 'Water Management', 'Uncover the essentials of effective water management at our workshop. From understanding hydrological processes to implementing water-saving technologies and policies, we''ll cover a wide range of topics relevant to sustainable water use.'),
(9, 'Livestock Selection and Husbandry for Sheep', 'Join us for an interactive session focused on Livestock Selection and Husbandry for Sheep, where you''ll engage in hands-on activities, demonstrations, and discussions with experienced sheep producers.'),
(10, 'Livestock Selection and Husbandry for Cows', 'Get hands-on experience and expert guidance in cow husbandry at our workshop. From proper milking techniques to calving assistance and herd health monitoring, equip yourself with the skills and knowledge needed to succeed in cow farming.'),
(11, 'Livestock Selection and Husbandry for Chicken', 'Uncover the fundamentals of successful chicken farming at our workshop. From understanding chicken behavior to designing and maintaining chicken coops and runs, we''ll provide practical guidance for raising chickens in any setting.'),
(12, 'Livestock Selection and Husbandry for Alpacas', 'Ensure your alpaca farming practices align with industry standards and best practices by attending our workshop. Discover techniques for cria care, herd management, and fiber marketing to maximize the success of your alpaca operation.'),
(13, 'Livestock Selection and Husbandry for Pigs', 'Calling all pig farmers and swine enthusiasts! Don''t miss our workshop dedicated to Livestock Selection and Husbandry for Pigs. Explore the characteristics of various pig breeds, breeding techniques, and tips for successful pig farming.'),
(14, 'Livestock Selection and Husbandry for Goats', 'Join us for an engaging workshop on livestock selection and husbandry for goats! Learn about different goat breeds, selecting quality breeding stock, and best practices for goat management.'),
(15, 'Livestock Selection and Husbandry for Dogs', 'Ensure your working dog management practices align with industry standards and best practices by attending our workshop. Discover techniques for socialization, obedience training, and managing working dog tasks to enhance livestock handling efficiency and safety.');

INSERT INTO lesson_info VALUES
(1, 'Animal Teeth Care', 'Discover the secrets to keeping your pets'' teeth healthy and strong with our Animal Teeth Care workshop. Our experts will share valuable tips and techniques for proper dental care.'),
(2, 'Animal Feet Care', 'Join us for an interactive session focused on Animal Feet Care, where you''ll learn how to inspect your pet''s paws, recognize potential issues, and implement preventive measures.'),
(3, 'Field Trips', 'Explore the world outside the classroom walls with our Field Trips workshop. Learn about different types of excursions, safety protocols, and ways to integrate real-world experiences into your curriculum.'),
(4, 'Legal Requirements', 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.'),
(5, 'Breeding', 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.'),
(6, 'Genetics', 'Calling all science enthusiasts! Don''t miss our workshop dedicated to Genetics. Discover how genes influence traits, diseases, and evolutionary processes, and how genetic technologies shape our understanding of life.'),
(7, 'Crops', 'Dive into the art and science of crop production with our workshop. Gain insights into soil management, crop rotation, pest and disease control, and other key aspects of successful crop cultivation.'),
(8, 'Water Management', 'Uncover the essentials of effective water management at our workshop. From understanding hydrological processes to implementing water-saving technologies and policies, we''ll cover a wide range of topics relevant to sustainable water use.'),
(9, 'Livestock Selection and Husbandry for Sheep', 'Join us for an interactive session focused on Livestock Selection and Husbandry for Sheep, where you''ll engage in hands-on activities, demonstrations, and discussions with experienced sheep producers.'),
(10, 'Livestock Selection and Husbandry for Cows', 'Get hands-on experience and expert guidance in cow husbandry at our workshop. From proper milking techniques to calving assistance and herd health monitoring, equip yourself with the skills and knowledge needed to succeed in cow farming.'),
(11, 'Livestock Selection and Husbandry for Chicken', 'Uncover the fundamentals of successful chicken farming at our workshop. From understanding chicken behavior to designing and maintaining chicken coops and runs, we''ll provide practical guidance for raising chickens in any setting.'),
(12, 'Livestock Selection and Husbandry for Alpacas', 'Ensure your alpaca farming practices align with industry standards and best practices by attending our workshop. Discover techniques for cria care, herd management, and fiber marketing to maximize the success of your alpaca operation.'),
(13, 'Livestock Selection and Husbandry for Pigs', 'Calling all pig farmers and swine enthusiasts! Don''t miss our workshop dedicated to Livestock Selection and Husbandry for Pigs. Explore the characteristics of various pig breeds, breeding techniques, and tips for successful pig farming.'),
(14, 'Livestock Selection and Husbandry for Goats', 'Join us for an engaging workshop on livestock selection and husbandry for goats! Learn about different goat breeds, selecting quality breeding stock, and best practices for goat management.'),
(15, 'Livestock Selection and Husbandry for Dogs', 'Ensure your working dog management practices align with industry standards and best practices by attending our workshop. Discover techniques for socialization, obedience training, and managing working dog tasks to enhance livestock handling efficiency and safety.');


INSERT INTO location VALUES
(1, 'Hall 1', 'Lincoln University', NULL, 200),
(2, 'Hall 2', 'Lincoln University', NULL, 250),
(3, 'Hall 3', 'Lincoln University', NULL, 100),
(4, 'Hall 4', 'Lincoln University', NULL, 200),
(5, 'Area 1', 'Lincoln University', NULL, 100),
(6, 'Online', NULL, NULL, NULL);

INSERT INTO subscription VALUES
(1, 'M', 5, 30),
(2, 'Y', 50, 30),
(3, 'L', 100, NULL);

-- INSERT INTO image VALUES
-- (7, 21, 'e8569b4f_Stuart-Charters__FocusFillWzE2MCwyMDAsIngiLDBd.jpg'),
-- (8, 22, '985ecb58_Roger-Dawson.jpg'),
-- (9, 23, '7b282e80_Sarah-Fraser.jpg');


INSERT INTO workshop VALUES
(1, 21, 1, 'Join us for an informative workshop on the importance of dental care for animals. In this workshop, participants will learn about the significance of maintaining good dental hygiene in pets and other animals. Topics covered will include: 1. Understanding the anatomy of animal teeth. 2. Common dental issues in pets and how to recognize them. 3. Best practices for brushing and cleaning animal teeth. 4. Importance of regular dental check-ups for animals. 5. Diet and nutrition tips for promoting healthy teeth in animals. 6. Tips for overcoming challenges in maintaining animal dental health. 7. Q&A session with experienced veterinarians and animal care experts. Whether you\'re a pet owner, animal enthusiast, or veterinary professional, this workshop will provide valuable insights and practical tips for ensuring the well-being of your furry friends. Don\'t miss this opportunity to learn how to keep animal smiles bright and healthy!', '2024-03-25', '09:00:00', 1, 250, 200, NULL),
(2, 21, 1, 'Join us for an informative workshop on the importance of dental care for animals. In this workshop, participants will learn about the significance of maintaining good dental hygiene in pets and other animals. Topics covered will include: 1. Understanding the anatomy of animal teeth. 2. Common dental issues in pets and how to recognize them. 3. Best practices for brushing and cleaning animal teeth. 4. Importance of regular dental check-ups for animals. 5. Diet and nutrition tips for promoting healthy teeth in animals. 6. Tips for overcoming challenges in maintaining animal dental health. 7. Q&A session with experienced veterinarians and animal care experts. Whether you\'re a pet owner, animal enthusiast, or veterinary professional, this workshop will provide valuable insights and practical tips for ensuring the well-being of your furry friends. Don\'t miss this opportunity to learn how to keep animal smiles bright and healthy!', '2024-03-27', '09:00:00', 1, 250, 200, NULL),
(3, 21, 1, 'Join us for an informative workshop on the importance of dental care for animals. In this workshop, participants will learn about the significance of maintaining good dental hygiene in pets and other animals. Topics covered will include: 1. Understanding the anatomy of animal teeth. 2. Common dental issues in pets and how to recognize them. 3. Best practices for brushing and cleaning animal teeth. 4. Importance of regular dental check-ups for animals. 5. Diet and nutrition tips for promoting healthy teeth in animals. 6. Tips for overcoming challenges in maintaining animal dental health. 7. Q&A session with experienced veterinarians and animal care experts. Whether you\'re a pet owner, animal enthusiast, or veterinary professional, this workshop will provide valuable insights and practical tips for ensuring the well-being of your furry friends. Don\'t miss this opportunity to learn how to keep animal smiles bright and healthy!', '2024-03-29', '09:00:00', 1, 250, 200, NULL),
(4, 22, 2, 'Join us for an interactive session focused on Animal Feet Care, where you''ll learn how to inspect your pet''s paws, recognize potential issues, and implement preventive measures.', '2024-03-27', '10:00:00', 2, 300, 250, NULL),
(5, 22, 2, 'Join us for an interactive session focused on Animal Feet Care, where you''ll learn how to inspect your pet''s paws, recognize potential issues, and implement preventive measures.', '2024-03-27', '14:00:00', 2, 300, 250, NULL),
(6, 23, 3, 'Explore the world outside the classroom walls with our Field Trips workshop. Learn about different types of excursions, safety protocols, and ways to integrate real-world experiences into your curriculum.', '2024-03-25', '9:00:00', 5, 300, 100, NULL),
(7, 23, 3, 'Explore the world outside the classroom walls with our Field Trips workshop. Learn about different types of excursions, safety protocols, and ways to integrate real-world experiences into your curriculum.', '2024-03-26', '9:00:00', 5, 300, 100, NULL),
(8, 23, 3, 'Explore the world outside the classroom walls with our Field Trips workshop. Learn about different types of excursions, safety protocols, and ways to integrate real-world experiences into your curriculum.', '2024-03-27', '9:00:00', 5, 300, 100, NULL),
(9, 23, 4, 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.', '2024-03-26', '13:00:00', 3, 450, 100, NULL),
(10, 23, 4, 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.', '2024-03-27', '13:00:00', 3, 450, 100, NULL),
(11, 23, 4, 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.', '2024-03-28', '13:00:00', 3, 450, 100, NULL),
(12, 23, 4, 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.', '2024-03-29', '13:00:00', 3, 450, 100, NULL),
(13, 23, 4, 'Calling all professionals! Don''t miss our workshop dedicated to Legal Requirements. Explore critical legal considerations, potential risks, and strategies for mitigating legal challenges in your field.', '2024-03-30', '13:00:00', 3, 450, 100, NULL),
(14, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-26', '10:00:00', 4, 350, 200, NULL),
(15, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-27', '10:00:00', 4, 350, 200, NULL),
(16, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-28', '10:00:00', 4, 350, 200, NULL),
(17, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-29', '10:00:00', 4, 350, 200, NULL),
(18, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-30', '10:00:00', 4, 350, 200, NULL),
(19, 24, 5, 'Dive into the art and science of animal breeding with our workshop. Gain insights into selective breeding, genetic diversity, and strategies for improving desirable traits in your breeding program.', '2024-03-29', '10:00:00', 4, 350, 200, NULL),
(20, 24, 6, 'Calling all science enthusiasts! Don''t miss our workshop dedicated to Genetics. Discover how genes influence traits, diseases, and evolutionary processes, and how genetic technologies shape our understanding of life.', '2024-03-26', '11:00:00', 1, 320, 200, NULL);

INSERT INTO lesson VALUES
(1, 9, 21, 6, '2024-03-26', '14:00:00', True, NULL, NULL),
(2, 10, 21, 6, '2024-03-27', '14:00:00', True, NULL, NULL),
(3, 11, 21, 6, '2024-03-28', '14:00:00', True, NULL, NULL),
(4, 12, 21, 6, '2024-03-29', '14:00:00', True, NULL, NULL),
(5, 13, 21, 6, '2024-03-30', '14:00:00', True, NULL, NULL),
(6, 1, 21, 6, '2024-03-26', '15:00:00', True, NULL, NULL),
(7, 2, 21, 6, '2024-03-27', '15:00:00', True, NULL, NULL),
(8, 3, 21, 6, '2024-03-28', '15:00:00', True, NULL, NULL),
(9, 4, 21, 6, '2024-03-29', '15:00:00', True, NULL, NULL),
(10, 5, 21, 6, '2024-03-30', '15:00:00', True, NULL, NULL),
(11, 1, 22, 6, '2024-03-26', '13:00:00', True, NULL, NULL),
(12, 2, 23, 6, '2024-03-27', '10:00:00', True, NULL, NULL),
(13, 3, 24, 6, '2024-03-28', '11:00:00', True, NULL, NULL),
(14, 4, 25, 6, '2024-03-29', '10:00:00', True, NULL, NULL),
(15, 5, 22, 6, '2024-03-30', '11:00:00', True, NULL, NULL),
(16, 1, 22, 6, '2024-03-26', '13:00:00', True, NULL, NULL),
(17, 2, 24, 6, '2024-03-28', '14:00:00', True, NULL, NULL),
(18, 3, 23, 6, '2024-03-28', '13:00:00', True, NULL, NULL),
(19, 4, 22, 6, '2024-03-29', '15:00:00', True, NULL, NULL),
(20, 5, 23, 6, '2024-03-30', '15:00:00', True, NULL, NULL),
(21, 2, 24, 6, '2024-03-27', '14:00:00', True, NULL, NULL),
(22, 3, 25, 6, '2024-03-28', '13:00:00', True, NULL, NULL),
(23, 4, 25, 6, '2024-03-29', '15:00:00', True, NULL, NULL),
(24, 5, 25, 6, '2024-03-30', '15:00:00', True, NULL, NULL);


INSERT INTO booking (booking_member_id, booking_lesson_id, booking_staff_id, booking_date)
VALUES
(1, 1, 21, CURDATE()),
(2, 2, 21, CURDATE()),
(3, 3, 21, CURDATE()),
(4, 4, 21, CURDATE()),
(1, 5, 21, CURDATE()),
(2, 6, 21, CURDATE()),
(3, 7, 21, CURDATE()),
(4, 8, 21, CURDATE()),
(2, 9, 21, CURDATE()),
(3, 10, 21, CURDATE()),
(2, 11, 22, CURDATE()),
(3, 12, 23, CURDATE()),
(2, 13, 24, CURDATE()),
(3, 14, 25, CURDATE());

INSERT INTO booking (booking_member_id, booking_workshop_id, booking_staff_id, booking_date)
VALUES
(1, 1, 21, CURDATE()),
(2, 2, 21, CURDATE()),
(3, 3, 21, CURDATE()),
(4, 4, 22, CURDATE()),
(1, 5, 22, CURDATE()),
(2, 6, 23, CURDATE()),
(3, 7, 23, CURDATE()),
(4, 8, 23, CURDATE()),
(2, 9, 23, CURDATE()),
(3, 10, 23, CURDATE()),
(2, 11, 23, CURDATE()),
(3, 12, 23, CURDATE()),
(2, 13, 23, CURDATE()),
(3, 14, 24, CURDATE());


INSERT INTO payment (payment_type, payment_lesson_id, payment_date, payment_payor_id, payment_amount)
VALUES
('C', 1, CURDATE(), 1, 100),
('C', 2, CURDATE(), 2, 100),
('C', 3, CURDATE(), 3, 100),
('C', 4, CURDATE(), 4, 100),
('C', 5, CURDATE(), 1, 100),
('C', 6, CURDATE(), 2, 100),
('C', 7, CURDATE(), 3, 100),
('C', 8, CURDATE(), 4, 100),
('C', 9, CURDATE(), 2, 100),
('C', 10, CURDATE(), 3, 100),
('C', 11, CURDATE(), 5, 100),
('C', 12, CURDATE(), 6, 100),
('C', 13, CURDATE(), 7, 100),
('C', 14, CURDATE(), 8, 100);

INSERT INTO news (new_title, news_text, news_image, news_uploaded) 
VALUES ('A warm welcome to all our new members', 'Welcome to Lifestyle Farming Club, we hope you have a fun and rewarding experience. From LLCMS Team', 'Lifestyle_Farming.jpg', '2009-12-01 12:00:00'),
       ('New Tutor Introduction', 'James Frank has 8 years of experience in farming. He is hoping to share his knowledge with the wider community', 'f33e5044_image.jpg', '2010-06-20 09:30:00'),
       ('New Member Introduction', 'Sally Richmond has recently retired from work within the corporate industry. She is looking to expand her knowledge around lifestyle farming and hoping to look after her farm as part of her retirement 	plan. A big warm welcome to Sally from the LLCMS Community', 'fbeb91cc_Sarah-Fraser.jpg', '2018-02-15 08:00:00'),
       ('Celebrating 10 years of LLCMS', 'LLCMS has achieved a new milestone. Thank you to each and everyone involved with helping us achieve this!', 'ten_years.jpg' , '2024-01-01 12:00:00');
