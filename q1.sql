SELECT Day_Requested, Shift_Requested, COUNT(Dog_ID) AS num_of_dogs
FROM Walk_App
WHERE Status="approved"
GROUP BY Day_Requested, Shift_Requested
HAVING COUNT(DISTINCT Walker_Email) >= 5
ORDER BY FIELD(day_requested, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
		 FIELD(shift_requested,'morning','afternoon','evening' );