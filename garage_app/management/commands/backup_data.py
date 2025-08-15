import os
import shutil
import gzip
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Créer une sauvegarde complète de la base de données et des fichiers média'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Répertoire de destination pour les sauvegardes (défaut: backups)'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compresser les sauvegardes avec gzip'
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Nombre de jours de sauvegardes à conserver (défaut: 30)'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Inclure les fichiers média dans la sauvegarde'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Mode silencieux - afficher seulement les erreurs'
        )

    def handle(self, *args, **options):
        self.verbosity = 0 if options['quiet'] else 1
        self.output_dir = Path(options['output_dir'])
        self.compress = options['compress']
        self.keep_days = options['keep_days']
        self.include_media = options['include_media']
        
        # Créer le répertoire de sauvegarde s'il n'existe pas
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Générer un nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'markev_backup_{timestamp}'
        
        try:
            self.log_info(f'🚀 Début de la sauvegarde: {backup_name}')
            
            # Créer un répertoire temporaire pour cette sauvegarde
            backup_dir = self.output_dir / backup_name
            backup_dir.mkdir(exist_ok=True)
            
            # Sauvegarder la base de données
            self.backup_database(backup_dir)
            
            # Sauvegarder les fichiers média si demandé
            if self.include_media:
                self.backup_media(backup_dir)
            
            # Créer un fichier d'informations sur la sauvegarde
            self.create_backup_info(backup_dir)
            
            # Compresser si demandé
            if self.compress:
                self.compress_backup(backup_dir)
            
            # Nettoyer les anciennes sauvegardes
            self.cleanup_old_backups()
            
            self.log_success(f'✅ Sauvegarde terminée avec succès: {backup_name}')
            
        except Exception as e:
            self.log_error(f'❌ Erreur lors de la sauvegarde: {str(e)}')
            raise CommandError(f'Échec de la sauvegarde: {str(e)}')

    def backup_database(self, backup_dir):
        """Sauvegarder la base de données"""
        self.log_info('📊 Sauvegarde de la base de données...')
        
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            self.backup_sqlite(backup_dir, db_config)
        elif db_config['ENGINE'] == 'django.db.backends.postgresql':
            self.backup_postgresql(backup_dir, db_config)
        else:
            raise CommandError(f"Type de base de données non supporté: {db_config['ENGINE']}")

    def backup_sqlite(self, backup_dir, db_config):
        """Sauvegarder une base de données SQLite"""
        source_db = Path(db_config['NAME'])
        target_db = backup_dir / 'database.sqlite3'
        
        if source_db.exists():
            # Utiliser la méthode de sauvegarde SQLite pour éviter les verrous
            source_conn = sqlite3.connect(str(source_db))
            target_conn = sqlite3.connect(str(target_db))
            
            source_conn.backup(target_conn)
            
            source_conn.close()
            target_conn.close()
            
            self.log_info(f'✓ Base de données SQLite sauvegardée: {target_db}')
        else:
            raise CommandError(f"Fichier de base de données introuvable: {source_db}")

    def backup_postgresql(self, backup_dir, db_config):
        """Sauvegarder une base de données PostgreSQL"""
        dump_file = backup_dir / 'database.sql'
        
        # Construire la commande pg_dump
        cmd = [
            'pg_dump',
            '--host', db_config.get('HOST', 'localhost'),
            '--port', str(db_config.get('PORT', 5432)),
            '--username', db_config['USER'],
            '--dbname', db_config['NAME'],
            '--file', str(dump_file),
            '--verbose',
            '--no-password'
        ]
        
        # Définir le mot de passe via variable d'environnement
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode != 0:
                raise CommandError(f"Erreur pg_dump: {result.stderr}")
            
            self.log_info(f'✓ Base de données PostgreSQL sauvegardée: {dump_file}')
        except FileNotFoundError:
            raise CommandError("pg_dump non trouvé. Assurez-vous que PostgreSQL est installé.")

    def backup_media(self, backup_dir):
        """Sauvegarder les fichiers média"""
        self.log_info('📁 Sauvegarde des fichiers média...')
        
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and any(media_root.iterdir()):
            media_backup_dir = backup_dir / 'media'
            shutil.copytree(media_root, media_backup_dir)
            self.log_info(f'✓ Fichiers média sauvegardés: {media_backup_dir}')
        else:
            self.log_info('ℹ️ Aucun fichier média à sauvegarder')

    def create_backup_info(self, backup_dir):
        """Créer un fichier d'informations sur la sauvegarde"""
        info_file = backup_dir / 'backup_info.txt'
        
        db_config = settings.DATABASES['default']
        
        info_content = f"""INFORMATIONS DE SAUVEGARDE MARKEV
=====================================

Date de création: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version Django: {settings.SECRET_KEY[:10]}...
Base de données: {db_config['ENGINE']}
Nom de la DB: {db_config.get('NAME', 'N/A')}
Fichiers média inclus: {'Oui' if self.include_media else 'Non'}
Compression: {'Oui' if self.compress else 'Non'}

Contenu de la sauvegarde:
- Base de données (database.sqlite3 ou database.sql)
{f'- Fichiers média (dossier media/)' if self.include_media else ''}
- Ce fichier d'informations

Pour restaurer cette sauvegarde:
1. Arrêter l'application Django
2. Remplacer la base de données actuelle
3. Restaurer les fichiers média si nécessaire
4. Redémarrer l'application

ATTENTION: Testez toujours la restauration sur un environnement de test d'abord!
"""
        
        info_file.write_text(info_content, encoding='utf-8')
        self.log_info(f'✓ Fichier d\'informations créé: {info_file}')

    def compress_backup(self, backup_dir):
        """Compresser la sauvegarde"""
        self.log_info('🗜️ Compression de la sauvegarde...')
        
        archive_path = f"{backup_dir}.tar.gz"
        
        # Créer l'archive tar.gz
        shutil.make_archive(str(backup_dir), 'gztar', backup_dir.parent, backup_dir.name)
        
        # Supprimer le répertoire non compressé
        shutil.rmtree(backup_dir)
        
        self.log_info(f'✓ Sauvegarde compressée: {archive_path}')

    def cleanup_old_backups(self):
        """Nettoyer les anciennes sauvegardes"""
        if self.keep_days <= 0:
            return
            
        self.log_info(f'🧹 Nettoyage des sauvegardes de plus de {self.keep_days} jours...')
        
        cutoff_date = datetime.now() - timedelta(days=self.keep_days)
        deleted_count = 0
        
        for item in self.output_dir.iterdir():
            if item.name.startswith('markev_backup_'):
                # Extraire la date du nom de fichier
                try:
                    date_str = item.name.split('_')[2]  # markev_backup_YYYYMMDD_HHMMSS
                    if len(date_str) >= 8:
                        backup_date = datetime.strptime(date_str[:8], '%Y%m%d')
                        if backup_date < cutoff_date:
                            if item.is_dir():
                                shutil.rmtree(item)
                            else:
                                item.unlink()
                            deleted_count += 1
                            self.log_info(f'🗑️ Supprimé: {item.name}')
                except (ValueError, IndexError):
                    # Ignorer les fichiers avec un format de nom incorrect
                    continue
        
        if deleted_count > 0:
            self.log_info(f'✓ {deleted_count} ancienne(s) sauvegarde(s) supprimée(s)')
        else:
            self.log_info('ℹ️ Aucune ancienne sauvegarde à supprimer')

    def log_info(self, message):
        """Afficher un message d'information"""
        if self.verbosity > 0:
            self.stdout.write(message)

    def log_success(self, message):
        """Afficher un message de succès"""
        if self.verbosity > 0:
            self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message):
        """Afficher un message d'erreur"""
        self.stderr.write(self.style.ERROR(message))
