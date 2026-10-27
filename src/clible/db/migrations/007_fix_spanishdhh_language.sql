-- Correct the catalog language code that earlier installs stored for Dios Habla Hoy.
UPDATE translations
SET language = 'es'
WHERE id = 'spanishdhh' AND language = 'en';
