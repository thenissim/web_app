SELECT d.Dog_ID, Dog_Name, wa.Walker_Email
FROM Walk_App AS wa 
JOIN Dog AS d ON wa.Dog_ID=d.Dog_ID 
WHERE Status="approved"
GROUP BY wa.Dog_ID, Dog_Name, wa.Walker_Email
HAVING COUNT(wa.Walker_Email) >= ALL((SELECT COUNT(wa2.Walker_Email)
								FROM Walk_App AS wa2  
								WHERE Status="approved"
								AND wa2.Dog_ID=d.Dog_ID
                                GROUP BY wa2.Dog_ID, wa2.Walker_Email));

