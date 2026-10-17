Create table Usuario_hostal(
	Id_Usuario_hostal INT primary key GENERATED ALWAYS AS IDENTITY,
	Nombres Varchar(250) not null,
	Apellidos Varchar(250) not null,
	Tipo_Documento varchar(50) not null,
	Numero_Documento varchar(50) not null,
	Fecha_Arrendamiento date not null,
	Lugar_Provenida varchar(250) not null,
	Lugar_Partida varchar(250) not null,
	fecha_Checkout TIMESTAMPTZ,
	constraint Documento_Numero Unique(Tipo_Documento,Numero_Documento)
);
