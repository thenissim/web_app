SELECT DISTINCT p.Walker_Email, Walker_Name, COUNT(DISTINCT Message_ID)
FROM Premium_Walker AS p 
JOIN Walk_App AS wa ON p.Walker_Email=wa.Walker_Email
JOIN Chat AS c ON p.Walker_Email=c.Walker_Email AND wa.Owner_Email=c.Owner_Email
JOIN Dog_Walker AS dw ON p.Walker_Email=dw.Walker_Email
WHERE YEAR(Prem_Reg_Date)="2021"
AND Status="approved"
GROUP BY p.Walker_Email, Walker_Name
ORDER BY COUNT(DISTINCT Message_ID) DESC;
