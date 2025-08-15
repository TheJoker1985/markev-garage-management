import os
import shutil
import tarfile
import sqlite3
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Restaurer une sauvegarde de la base de données et des fichiers média'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_path',
            type=str,
            help='Chemin vers la sauvegarde à restaurer (dossier ou archive .tar.gz)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la restauration sans confirmation'
        )
        parser.add_argument(
            '--restore-media',
            action='store_true',
            help='Restaurer également les fichiers média'
        )
        parser.add_argument(
            '--backup-current',
            action='store_true',
            help='Créer une sauvegarde des données actuelles avant restauration'
        )

    def handle(self, *args, **options):
        backup_path = Path(options['backup_path'])
        self.force = options['force']
        self.restore_media = options['restore_media']
        self.backup_current = options['backup_current']
        
        if not backup_path.exists():
            raise CommandError(f"Sauvegarde introuvable: {backup_path}")
        
        try:
            # Vérifier et préparer la sauvegarde
            backup_dir = self.prepare_backup(backup_path)
            
            # Afficher les informations de la sauvegarde
            self.show_backup_info(backup_dir)
            
            # Demander confirmation si pas forcé
            if not self.force:
                if not self.confirm_restore():
                    self.stdout.write('❌ Restauration annulée par l\'utilisateur')
                    return
            
            # Sauvegarder les données actuelles si demandé
            if self.backup_current:
                self.create_current_backup()
            
            # Restaurer la base de données
            self.restore_database(backup_dir)
            
            # Restaurer les fichiers média si demandé
            if self.restore_media:
                self.restore_media_files(backup_dir)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Restauration terminée avec succès!')
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ N\'oubliez pas de redémarrer l\'application Django'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Erreur lors de la restauration: {str(e)}')

    def prepare_backup(self, backup_path):
        """Préparer la sauvegarde pour restauration"""
        if backup_path.is_file() and backup_path.suffix == '.gz':
            # Extraire l'archive
            self.stdout.write('📦 Extraction de l\'archive de sauvegarde...')
            extract_dir = backup_path.parent / 'temp_restore'
            
            # Supprimer le répertoire temporaire s'il existe
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            extract_dir.mkdir()
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            
            # Trouver le répertoire de sauvegarde extrait
            extracted_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise CommandError("Aucun répertoire trouvé dans l'archive")
            
            return extracted_dirs[0]
        
        elif backup_path.is_dir():
            return backup_path
        
        else:
            raise CommandError("Format de sauvegarde non reconnu")

    def show_backup_info(self, backup_dir):
        """Afficher les informations de la sauvegarde"""
        info_file = backup_dir / 'backup_info.txt'
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📋 INFORMATIONS DE LA SAUVEGARDE')
        self.stdout.write('='*50)
        
        if info_file.exists():
            content = info_file.read_text(encoding='utf-8')
            self.stdout.write(content)
        else:
            self.stdout.write('ℹ️ Aucun fichier d\'informations trouvé')
            
            # Lister le contenu du répertoire
            self.stdout.write('\n📁 Contenu de la sauvegarde:')
            for item in backup_dir.iterdir():
                self.stdout.write(f'  - {item.name}')
        
        self.stdout.write('='*50 + '\n')

    def confirm_restore(self):
        """Demander confirmation à l'utilisateur"""
        self.stdout.write(
            self.style.WARNING(
                '⚠️ ATTENTION: Cette opération va remplacer vos données actuelles!'
            )
        )
        self.stdout.write(
            'Les données actuelles seront perdues si vous n\'avez pas fait de sauvegarde.'
        )
        
        response = input('\nÊtes-vous sûr de vouloir continuer? (oui/non): ')
        return response.lower() in ['oui', 'o', 'yes', 'y']

    def create_current_backup(self):
        """Créer une sauvegarde des données actuelles"""
        self.stdout.write('💾 Création d\'une sauvegarde des données actuelles...')
        
        from django.core.management import call_command
        
        try:
            call_command(
                'backup_data',
                '--output-dir', 'backups/pre_restore',
                '--compress',
                '--include-media',
                '--quiet'
            )
            self.stdout.write('✓ Sauvegarde actuelle créée dans backups/pre_restore/')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Impossible de créer la sauvegarde actuelle: {e}')
            )

    def restore_database(self, backup_dir):
        """Restaurer la base de données"""
        self.stdout.write('📊 Restauration de la base de données...')
        
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            self.restore_sqlite(backup_dir, db_config)
        elif db_config['ENGINE'] == 'django.db.backends.postgresql':
            self.restore_postgresql(backup_dir, db_config)
        else:
            raise CommandError(f"Type de base de données non supporté: {db_config['ENGINE']}")

    def restore_sqlite(self, backup_dir, db_config):
        """Restaurer une base de données SQLite"""
        backup_db = backup_dir / 'database.sqlite3'
        target_db = Path(db_config['NAME'])
        
        if not backup_db.exists():
            raise CommandError(f"Fichier de sauvegarde SQLite introuvable: {backup_db}")
        
        # Sauvegarder l'ancienne base si elle existe
        if target_db.exists():
            backup_old = target_db.with_suffix('.sqlite3.old')
            shutil.copy2(target_db, backup_old)
            self.stdout.write(f'✓ Ancienne base sauvegardée: {backup_old}')
        
        # Copier la nouvelle base
        shutil.copy2(backup_db, target_db)
        self.stdout.write(f'✓ Base de données SQLite restaurée: {target_db}')

    def restore_postgresql(self, backup_dir, db_config):
        """Restaurer une base de données PostgreSQL"""
        dump_file = backup_dir / 'database.sql'
        
        if not dump_file.exists():
            raise CommandError(f"Fichier de sauvegarde PostgreSQL introuvable: {dump_file}")
        
        # Construire la commande psql pour restaurer
        cmd = [
            'psql',
            '--host', db_config.get('HOST', 'localhost'),
            '--port', str(db_config.get('PORT', 5432)),
            '--username', db_config['USER'],
            '--dbname', db_config['NAME'],
            '--file', str(dump_file),
            '--quiet'
        ]
        
        # Définir le mot de passe via variable d'environnement
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        try:
            # D'abord, vider la base de données existante
            self.stdout.write('🗑️ Nettoyage de la base de données existante...')
            
            # Commande pour supprimer toutes les tables
            drop_cmd = [
                'psql',
                '--host', db_config.get('HOST', 'localhost'),
                '--port', str(db_config.get('PORT', 5432)),
                '--username', db_config['USER'],
                '--dbname', db_config['NAME'],
                '--command', 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
            ]
            
            result = subprocess.run(drop_cmd, env=env, capture_output=True, text=True)
            if result.returncode != 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Avertissement lors du nettoyage: {result.stderr}')
                )
            
            # Restaurer depuis le dump
            self.stdout.write('📥 Restauration depuis le fichier de sauvegarde...')
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f"Erreur lors de la restauration: {result.stderr}")
            
            self.stdout.write('✓ Base de données PostgreSQL restaurée')
            
        except FileNotFoundError:
            raise CommandError("psql non trouvé. Assurez-vous que PostgreSQL est installé.")

    def restore_media_files(self, backup_dir):
        """Restaurer les fichiers média"""
        self.stdout.write('📁 Restauration des fichiers média...')
        
        media_backup_dir = backup_dir / 'media'
        media_root = Path(settings.MEDIA_ROOT)
        
        if not media_backup_dir.exists():
            self.stdout.write('ℹ️ Aucun fichier média dans la sauvegarde')
            return
        
        # Sauvegarder les fichiers média actuels
        if media_root.exists() and any(media_root.iterdir()):
            media_backup = media_root.with_name(f'{media_root.name}_backup')
            if media_backup.exists():
                shutil.rmtree(media_backup)
            shutil.copytree(media_root, media_backup)
            self.stdout.write(f'✓ Fichiers média actuels sauvegardés: {media_backup}')
        
        # Supprimer les fichiers média actuels
        if media_root.exists():
            shutil.rmtree(media_root)
        
        # Copier les fichiers média de la sauvegarde
        shutil.copytree(media_backup_dir, media_root)
        self.stdout.write(f'✓ Fichiers média restaurés: {media_root}')

    def cleanup_temp_files(self):
        """Nettoyer les fichiers temporaires"""
        temp_dir = Path('temp_restore')
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
