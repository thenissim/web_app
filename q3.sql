SELECT DISTINCT dw.Walker_Name, dw.Walker_Email
FROM Dog AS d
JOIN Walk_App AS wa ON d.Dog_ID=wa.Dog_ID
JOIN Dog_Walker AS dw ON dw.Walker_Email=wa.Walker_Email
WHERE dw.Walker_Email NOT IN (SELECT wa1.Walker_Email FROM Dog_Walker AS dw1
								JOIN Walk_App AS wa1 
                                ON dw1.Walker_Email=wa1.Walker_Email
                                JOIN Dog AS d
                                ON d.Dog_ID=wa1.Dog_ID
                                WHERE Is_Vaccined="no"
                                OR Is_Friendly="no")
AND wa.Status="approved";