CREATE DATABASE agrovision;
USE agrovision;

CREATE TABLE usuarios (
	UsuarioID INT NOT NULL AUTO_INCREMENT,
    Nombre VARCHAR(255) NOT NULL,
    Apellido VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    PRIMARY KEY (UsuarioID)
);

CREATE TABLE detecciones (
	DeteccionID INT NOT NULL AUTO_INCREMENT,
    Carrots INT NOT NULL,
    Eggplants INT NOT NULL,
    Potatoes INT NOT NULL,
    Tomatoes INT NOT NULL,
    Fecha DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Hora TIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UsuarioID INT NOT NULL,
    PRIMARY KEY (DeteccionID),
    FOREIGN KEY (UsuarioID) REFERENCES usuarios(UsuarioID)
);

CREATE VIEW vista_detecciones AS
SELECT 
	detecciones.DeteccionID AS DeteccionID,
    detecciones.Carrots AS Carrots,
    detecciones.Eggplants AS Eggplants,
    detecciones.Potatoes AS Potatoes,
    detecciones.Tomatoes AS Tomatoes,
    detecciones.Fecha AS Fecha,
    detecciones.Hora AS Hora,
    detecciones.UsuarioID AS UsuarioID,
    usuarios.Nombre AS Nombre,
    usuarios.Apellido AS Apellido
FROM detecciones
INNER JOIN usuarios ON detecciones.UsuarioID = usuarios.UsuarioID;

-- Super Admin
INSERT INTO usuarios (Nombre, Apellido, Email, Password) VALUES ("AgroVision", "Admin", "admin@agrovision.com", "AgroVision12345");

-- Usuario de Ejemplo
INSERT INTO usuarios (Nombre, Apellido, Email, Password) VALUES ("AgroVision", "Usuario de Ejemplo", "ejemplo@agrovision.com", "AgroVision12345");

